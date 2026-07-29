from src.bot.validators.phone import normalize_phone


def test_accepts_plain_digits():
    assert normalize_phone("12025550123") == "12025550123"


def test_accepts_plus_prefixed_and_strips_formatting():
    assert normalize_phone("+1 (202) 555-0123") == "+12025550123"


def test_rejects_too_short():
    assert normalize_phone("12345") is None


def test_rejects_leading_zero_country_code():
    # regex requires first digit after optional '+' to be 1-9
    assert normalize_phone("+0123456789") is None


def test_rejects_non_numeric_garbage():
    assert normalize_phone("not a phone number") is None


def test_rejects_empty_string():
    assert normalize_phone("") is None


def test_strips_surrounding_whitespace():
    assert normalize_phone("  +12025550123  ") == "+12025550123"
