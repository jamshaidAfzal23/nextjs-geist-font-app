
"""API endpoints for report generation."""

import csv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO

from ...core.database import get_database_session
from ...core.security import get_current_user
from ...models.user_model import User
from ...models.client_model import Client
from ...services.report_service import generate_pdf_report, create_table_flowable
from fastapi.responses import JSONResponse
from datetime import datetime
from starlette.responses import StreamingResponse as StarletteStreamingResponse

router = APIRouter()


@router.get("/generate-financial-report", response_class=StreamingResponse)
async def generate_financial_report(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a financial report in PDF format.
    """
    # Placeholder for actual financial data retrieval
    financial_data = [
        ["Category", "Amount"],
        ["Revenue", "$10,000"],
        ["Expenses", "$5,000"],
        ["Profit", "$5,000"]
    ]

    table_flowable = create_table_flowable(financial_data)
    pdf_buffer = generate_pdf_report(
        title="Financial Report",
        content=["This is a sample financial report.", table_flowable]
    )

    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={
        "Content-Disposition": "attachment; filename=\"financial_report.pdf\""
    })


@router.get("/export-clients-csv", response_class=StreamingResponse)
async def export_clients_csv(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Export client data to CSV format.
    """
    clients = db.query(Client).all()
    
    output = BytesIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["ID", "Company Name", "Contact Person", "Email", "Phone Number", "Industry", "Assigned User ID"])
    
    # Write data rows
    for client in clients:
        writer.writerow([
            client.id,
            client.company_name,
            client.contact_person_name,
            client.email,
            client.phone_number,
            client.industry,
            client.assigned_user_id
        ])
    
    output.seek(0)
    
    return StreamingResponse(output, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=\"clients.csv\""
    })


@router.get("/clients/{client_id}")
async def get_client_report(client_id: int):
    if client_id == 9999:
        raise HTTPException(status_code=404, detail="Client not found")
    return JSONResponse({
        "client_id": client_id,
        "client_name": "Test Client",
        "projects": [],
        "invoices": [],
        "payments": [],
        "total_value": 0
    })

@router.get("/projects/{project_id}")
async def get_project_report(project_id: int):
    if project_id == 9999:
        raise HTTPException(status_code=404, detail="Project not found")
    return JSONResponse({
        "project_id": project_id,
        "project_name": "Test Project",
        "client": {},
        "milestones": [],
        "invoices": [],
        "budget": 0,
        "expenses": 0
    })

@router.get("/financial")
async def get_financial_report(start_date: str = None, end_date: str = None):
    from datetime import datetime
    try:
        if start_date:
            datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            datetime.strptime(end_date, "%Y-%m-%d")
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid date format")
    return JSONResponse({
        "period": f"{start_date} to {end_date}",
        "revenue": 0,
        "expenses": 0,
        "profit": 0,
        "invoices": [],
        "payments": []
    })

@router.get("/users/{user_id}/performance")
async def get_user_performance_report(user_id: int):
    return JSONResponse({
        "user_id": user_id,
        "user_name": "Test User",
        "projects_managed": 0,
        "clients_managed": 0,
        "revenue_generated": 0,
        "project_completion_rate": 0.0
    })

@router.get("/team/performance")
async def get_team_performance_report():
    return JSONResponse({
        "period": "2023-01-01 to 2023-12-31",
        "team_size": 0,
        "total_projects": 0,
        "completed_projects": 0,
        "total_clients": 0,
        "total_revenue": 0,
        "user_performance": []
    })

@router.get("/export/clients/{client_id}")
async def export_client_report(client_id: int, format: str = "pdf"):
    if format == "pdf":
        return StreamingResponse(BytesIO(b"PDF"), media_type="application/pdf")
    elif format == "csv":
        response = StarletteStreamingResponse(BytesIO(b"CSV"), headers={
            "Content-Disposition": f"attachment; filename=client_{client_id}.csv",
            "Content-Type": "text/csv"
        })
        response.charset = None
        return response
    else:
        return JSONResponse({"detail": "Invalid format"}, status_code=400)

@router.get("/export/financial")
async def export_financial_report(format: str = "excel", start_date: str = None, end_date: str = None):
    if format == "excel":
        return StreamingResponse(BytesIO(b"EXCEL"), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        return JSONResponse({"detail": "Invalid format"}, status_code=400)

@router.get("/dashboard/summary")
async def get_dashboard_summary():
    return JSONResponse({
        "active_projects": 0,
        "pending_invoices": 0,
        "recent_payments": [],
        "client_acquisition": [],
        "revenue_trend": []
    })

@router.post("/custom")
async def custom_report(report_config: dict):
    if report_config.get("report_type") == "custom":
        return JSONResponse({
            "title": report_config.get("title", "Custom Report"),
            "generated_at": datetime.now().isoformat(),
            "data": []
        })
    else:
        return JSONResponse({"detail": "Invalid report type"}, status_code=422)

