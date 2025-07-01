"""
Database backup service for the Smart CRM SaaS application.
"""

import shutil
from datetime import datetime
from pathlib import Path

from ..core.config import settings

def create_database_backup() -> str:
    """
    Creates a timestamped backup of the SQLite database file.
    Returns the path to the created backup file.
    """
    db_path = Path(settings.DATABASE_URL.replace("sqlite:///", ""))
    if not db_path.is_file():
        raise FileNotFoundError(f"Database file not found at {db_path}")

    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{db_path.stem}_backup_{timestamp}{db_path.suffix}"
    backup_path = backup_dir / backup_filename

    shutil.copy2(db_path, backup_path)
    return str(backup_path)
