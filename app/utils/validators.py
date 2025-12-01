import re


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def ensure_non_empty(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def ensure_email(value: str) -> str:
    value = ensure_non_empty(value, "email")
    if not _EMAIL_RE.match(value):
        raise ValueError("email is not valid")
    return value

def ensure_phone_number(value: str) -> str:
    value = ensure_non_empty(value, "phone")
    # Simple phone number validation (allows digits, spaces, dashes, parentheses, and plus sign)
    # Outputs as a sequence of digits only
    cleaned = re.sub(r"[^\d]", "", value)
    if len(cleaned) < 7 or len(cleaned) > 15:
        raise ValueError("phone number is not valid")
    return cleaned

def ensure_length_max(value: str, field: str, max_len: int) -> str:
    value = ensure_non_empty(value, field)
    if len(value) > max_len:
        raise ValueError(f"{field} must be at most {max_len} characters")
    return value
