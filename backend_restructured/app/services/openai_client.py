"""
OpenAI API client for the Smart CRM SaaS application.
"""

from openai import OpenAI
from ..core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_openai_client():
    return client
