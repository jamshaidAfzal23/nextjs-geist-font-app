"""
AI-powered API endpoints for Smart CRM SaaS application.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.database import get_database_session
from ...core.security import get_current_user
from ...models.user_model import User
from ...models.client_model import Client
from ...schemas.ai_schemas import (
    ClientAnalysisRequest, 
    ClientAnalysisResponse,
    FinancialAnalysisRequest,
    FinancialAnalysisResponse
)
from ...services.openai_client import get_openai_client

router = APIRouter()


@router.post("/client-analysis", response_model=ClientAnalysisResponse)
async def analyze_client(
    request: ClientAnalysisRequest,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Perform smart analysis on client data using AI.
    """
    client = db.query(Client).filter(Client.id == request.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    openai_client = get_openai_client()

    # Example: Generate a summary of the client
    if request.analysis_type == "summary":
        prompt = f"Summarize the following client information: Company Name: {client.company_name}, Contact Person: {client.contact_person_name}, Email: {client.email}, Industry: {client.industry}, Notes: {client.general_notes}"
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            summary = response.choices[0].message.content.strip()
            return ClientAnalysisResponse(
                client_id=client.id,
                analysis_type="summary",
                result=summary
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OpenAI API error: {e}"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid analysis type"
        )


@router.post("/financial-analysis", response_model=FinancialAnalysisResponse)
async def analyze_financial_data(
    request: FinancialAnalysisRequest,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Perform smart analysis on financial data using AI.
    """
    openai_client = get_openai_client()

    prompt = f"Analyze the following financial data for the period {request.start_date} to {request.end_date}: {request.data}. Provide a summary of the financial performance, identify key trends, and offer recommendations."
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        analysis_result = response.choices[0].message.content.strip()

        # You would parse the analysis_result to extract summary, trends, and recommendations
        # For simplicity, we'll just return the raw result for now.
        return FinancialAnalysisResponse(
            analysis_period=f"{request.start_date} to {request.end_date}",
            summary=analysis_result,
            key_trends=["Trend 1", "Trend 2"],  # Placeholder
            recommendations=["Recommendation 1", "Recommendation 2"]  # Placeholder
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OpenAI API error: {e}"
        )
