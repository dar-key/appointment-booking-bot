from src.bot.callback_data.booking import ServiceCb, TimeCb
from src.bot.constants import BOOKING_DAYS_AHEAD, SERVICES, TIME_SLOTS
from src.bot.keyboards.booking import (
    get_dates_keyboard,
    get_services_keyboard,
    get_start_keyboard,
    get_time_slots_keyboard,
)


def _flatten(markup):
    return [button for row in markup.inline_keyboard for button in row]


def _callback_data(button) -> str:
    assert button.callback_data is not None
    return button.callback_data


def test_start_keyboard_has_single_entry_button():
    markup = get_start_keyboard()
    buttons = _flatten(markup)
    assert len(buttons) == 1
    assert buttons[0].callback_data == "start_booking"


def test_services_keyboard_lists_every_configured_service():
    markup = get_services_keyboard()
    buttons = _flatten(markup)
    assert len(buttons) == len(SERVICES)
    assert [b.text for b in buttons] == SERVICES

    unpacked_names = [ServiceCb.unpack(_callback_data(b)).name for b in buttons]
    assert unpacked_names == SERVICES


def test_dates_keyboard_uses_relative_labels_for_first_two_days():
    markup = get_dates_keyboard()
    buttons = _flatten(markup)
    assert len(buttons) == BOOKING_DAYS_AHEAD
    assert buttons[0].text.startswith("Today")
    assert buttons[1].text.startswith("Tomorrow")


def test_time_slots_keyboard_marks_booked_slots_as_unavailable():
    booked = [TIME_SLOTS[0]]
    markup = get_time_slots_keyboard(booked, "2099-01-01")
    buttons = _flatten(markup)

    booked_button = buttons[0]
    assert "(Booked)" in booked_button.text
    assert _callback_data(booked_button) == "slot_unavailable"


def test_time_slots_keyboard_marks_past_slots_as_unavailable():
    markup = get_time_slots_keyboard([], "2000-01-01")
    buttons = _flatten(markup)

    for button in buttons:
        assert "(Past)" in button.text
        assert _callback_data(button) == "slot_unavailable"


def test_time_slots_keyboard_allows_free_future_slots():
    markup = get_time_slots_keyboard([], "2099-01-01")
    buttons = _flatten(markup)

    assert len(buttons) == len(TIME_SLOTS)
    for button, slot in zip(buttons, TIME_SLOTS):
        assert button.text == slot
        assert TimeCb.unpack(_callback_data(button)).time == slot.replace(":", "-")
