"""
AI schemas for Smart CRM SaaS application.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ClientAnalysisRequest(BaseModel):
    client_id: int = Field(..., description="ID of the client to analyze")
    analysis_type: str = Field(..., description="Type of analysis to perform (e.g., 'summary', 'sentiment')")

class ClientAnalysisResponse(BaseModel):
    client_id: int = Field(..., description="ID of the analyzed client", example=1)
    analysis_type: str = Field(..., description="Type of analysis performed", example="summary")
    result: str = Field(..., description="Result of the analysis", example="Acme Corp is a technology client with 2 active projects.")
    insights: Optional[List[str]] = Field(None, description="List of key insights generated", example=["High project volume", "Strong technology focus"])

class FinancialAnalysisRequest(BaseModel):
    start_date: str = Field(..., description="Start date for financial data (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date for financial data (YYYY-MM-DD)")
    data: Dict[str, float] = Field(..., description="Financial data to analyze (e.g., total_revenue, total_expenses)")

class FinancialAnalysisResponse(BaseModel):
    analysis_period: str = Field(..., description="Period of financial analysis", example="2023-01-01 to 2023-12-31")
    summary: str = Field(..., description="AI-generated summary of financial performance", example="The company showed strong revenue growth in 2023, with expenses well-managed.")
    key_trends: Optional[List[str]] = Field(None, description="Identified key financial trends", example=["Consistent revenue growth", "Stable expense ratio"])
    recommendations: Optional[List[str]] = Field(None, description="AI-generated recommendations", example=["Invest in marketing to accelerate growth", "Optimize operational costs"])