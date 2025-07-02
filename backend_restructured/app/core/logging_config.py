"""
Logging configuration for the Smart CRM SaaS application.
"""

import logging

def setup_logging():
    """
    Configures the logging for the application.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
