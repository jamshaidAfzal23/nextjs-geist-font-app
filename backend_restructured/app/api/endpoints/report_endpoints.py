
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

