import re

_PHONE_RE = re.compile(r"^\+?[1-9]\d{7,14}$")


def normalize_phone(raw: str) -> str | None:
    phone = raw.strip()
    digits = re.sub(r"\D", "", phone)
    normalized = f"+{digits}" if phone.startswith("+") else digits

    if not _PHONE_RE.fullmatch(normalized):
        return None

    return normalized
