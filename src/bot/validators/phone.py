import re

PHONE_RE = re.compile(r"^\+?[1-9]\d{1,14}$")


def is_valid_phone(phone: str) -> bool:
    digits = re.sub(r"\D", "", phone)
    return PHONE_RE.fullmatch(digits) is not None
