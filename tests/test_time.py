import datetime

from src.bot.utils.time import format_date_for_display, is_slot_in_past, now


def test_now_returns_timezone_aware_datetime():
    result = now()
    assert isinstance(result, datetime.datetime)
    assert result.tzinfo is not None


def test_slot_in_the_past_is_detected():
    assert is_slot_in_past("2000-01-01", "10:00 AM") is True


def test_slot_far_in_the_future_is_not_past():
    assert is_slot_in_past("2099-01-01", "10:00 AM") is False


def test_slot_boundary_exactly_now_counts_as_past():
    current = now()
    date_str = current.strftime("%Y-%m-%d")
    time_str = current.strftime("%I:%M %p")
    assert is_slot_in_past(date_str, time_str) is True


def test_format_date_for_display_uses_readable_format():
    assert format_date_for_display("2026-08-01") == "01 Aug 2026"


def test_format_date_for_display_handles_single_digit_day():
    assert format_date_for_display("2026-01-05") == "05 Jan 2026"
