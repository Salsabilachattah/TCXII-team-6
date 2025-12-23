from typing import Optional
from datetime import date, datetime


def generate_reference(ticket_id: int, category: Optional[str] = None, created_at: Optional[date] = None) -> str:
    if category:
        prefix = (category.strip()[:3].upper())
        if len(prefix) < 3:
            prefix = prefix.ljust(3, 'X')
    else:
        prefix = 'UNK'

    year = '0000'
    if created_at:
        try:
            if isinstance(created_at, (date, datetime)):
                year = f"{created_at.year:04d}"
            else:
                year = str(created_at)[:4]
        except Exception:
            year = '0000'

    try:
        num = int(ticket_id)
    except Exception:
        num = ticket_id

    return f"{prefix}-{year}-{int(num):06d}" if isinstance(num, int) else f"{prefix}-{year}-{num}"