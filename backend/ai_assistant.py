from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from openai_client import generate_text

router = APIRouter()

class AIRequest(BaseModel):
    action_type: str
    input_text: Optional[str] = None
    related_id: Optional[int] = None

class AIResponse(BaseModel):
    output_text: str

@router.post("/ai-assistant", response_model=AIResponse)
async def ai_assistant(request: AIRequest):
    if request.action_type == "message_summary":
        if not request.input_text:
            raise HTTPException(status_code=400, detail="input_text is required for message_summary")
        prompt = f"Summarize the following message:\n{request.input_text}"
        summary = await generate_text(prompt)
        return AIResponse(output_text=summary)
    elif request.action_type == "follow_up_reminder":
        if not request.related_id:
            raise HTTPException(status_code=400, detail="related_id is required for follow_up_reminder")
        prompt = f"Generate a follow-up reminder for related ID {request.related_id}."
        reminder = await generate_text(prompt)
        return AIResponse(output_text=reminder)
    elif request.action_type == "invoice_text_generation":
        if not request.related_id:
            raise HTTPException(status_code=400, detail="related_id is required for invoice_text_generation")
        prompt = f"Generate invoice text for related ID {request.related_id}."
        invoice_text = await generate_text(prompt)
        return AIResponse(output_text=invoice_text)
    else:
        return AIResponse(output_text="Invalid action_type")
