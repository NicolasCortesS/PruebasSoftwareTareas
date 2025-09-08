from datetime import datetime, timezone
from typing import Optional


def validate_non_empty(value: str) -> Optional[str]:
    v = value.strip()
    return v if v else None


def validate_price(value: str) -> Optional[float]:
    try:
        p = float(value)
        return p if p >= 0 else None
    except Exception:
        return None


def validate_int(value: str) -> Optional[int]:
    try:
        i = int(value)
        return i if i >= 0 else None
    except Exception:
        return None


def parse_local_datetime_to_utc(value: str) -> Optional[datetime]:
    """Parse a local datetime string into UTC-aware datetime.

    Accepts ISO or 'YYYY-MM-DD HH:MM'. Returns UTC datetime or None on error.
    """
    if not value:
        return None
    # Try ISO first
    try:
        dt = datetime.fromisoformat(value)
    except Exception:
        # Try YYYY-MM-DD HH:MM
        try:
            dt = datetime.strptime(value, "%Y-%m-%d %H:%M")
        except Exception:
            # Try DD-MM-YYYY HH:MM
            try:
                dt = datetime.strptime(value, "%d-%m-%Y %H:%M")
            except Exception:
                # Try DD-MM-YYYY (date only)
                try:
                    dt = datetime.strptime(value, "%d-%m-%Y")
                except Exception:
                    return None
    # if naive, assume local timezone
    if dt.tzinfo is None:
        dt = dt.astimezone()
    return dt.astimezone(timezone.utc)


def confirm_yes(value: str) -> bool:
    return value.strip().lower() in ("y", "s", "yes", "si")
