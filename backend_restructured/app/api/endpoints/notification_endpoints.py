"""
API endpoints for notifications.
"""

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_database_session
from ...core.security import get_current_user
from ...models.user_model import User
from ...models.notification_model import Notification
from ...schemas.notification_schemas import NotificationCreate, NotificationResponse, NotificationUpdate
from ...services.email_service import send_email

router = APIRouter()

class EmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    html_content: str
    plain_text_content: str = None

@router.post("/send-email", status_code=status.HTTP_200_OK)
async def send_notification_email(
    email_request: EmailRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send an email notification.
    """
    try:
        send_email(
            to_email=email_request.to_email,
            subject=email_request.subject,
            html_content=email_request.html_content,
            plain_text_content=email_request.plain_text_content
        )
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {e}"
        )


@router.post("/in-app", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_in_app_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new in-app notification.
    """
    db_notification = Notification(
        user_id=notification_data.user_id,
        title=notification_data.title,
        message=notification_data.message
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


@router.get("/in-app", response_model=List[NotificationResponse])
async def get_in_app_notifications(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
    is_read: Optional[bool] = None
):
    """
    Get in-app notifications for the current user.
    """
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    return query.all()


@router.put("/in-app/{notification_id}", response_model=NotificationResponse)
async def update_in_app_notification(
    notification_id: int,
    notification_data: NotificationUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update an in-app notification (e.g., mark as read).
    """
    notification = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    for field, value in notification_data.dict(exclude_unset=True).items():
        setattr(notification, field, value)
    
    db.commit()
    db.refresh(notification)
    return notification


@router.delete("/in-app/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_in_app_notification(
    notification_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an in-app notification.
    """
    notification = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    db.delete(notification)
    db.commit()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # You can process received data here if needed
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Client #{client_id} disconnected")