import os
import openai
from fastapi import HTTPException

# Load OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable not set")

openai.api_key = OPENAI_API_KEY

async def generate_text(prompt: str, max_tokens: int = 150) -> str:
    try:
        response = await openai.Completion.acreate(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.7,
            n=1,
            stop=None,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
