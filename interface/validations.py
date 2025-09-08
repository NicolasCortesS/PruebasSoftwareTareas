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
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except Exception:
        try:
            dt = datetime.strptime(value, "%Y-%m-%d %H:%M")
        except Exception:
            try:
                dt = datetime.strptime(value, "%d-%m-%Y %H:%M")
            except Exception:
                try:
                    dt = datetime.strptime(value, "%d-%m-%Y")
                except Exception:
                    return None
    if dt.tzinfo is None:
        dt = dt.astimezone()
    return dt.astimezone(timezone.utc)


def confirm_yes(value: str) -> bool:
    return value.strip().lower() in ("y", "s", "yes", "si")
