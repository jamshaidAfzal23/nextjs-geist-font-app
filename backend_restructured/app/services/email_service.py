"""
Email service for the Smart CRM SaaS application.
"""

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from ..core.config import settings

def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    plain_text_content: str = None
):
    """
    Sends an email using SendGrid.
    """
    message = Mail(
        from_email=settings.MAIL_FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    if plain_text_content:
        message.plain_text_content = plain_text_content

    try:
        sendgrid_client = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sendgrid_client.send(message)
        print(f"Email sent to {to_email}. Status Code: {response.status_code}")
        return response
    except Exception as e:
        print(f"Error sending email: {e}")
        raise
