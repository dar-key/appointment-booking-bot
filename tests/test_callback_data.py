from src.bot.callback_data.booking import DateCb, ServiceCb, TimeCb


def test_service_cb_round_trip():
    packed = ServiceCb(name="Haircut ($20)").pack()
    unpacked = ServiceCb.unpack(packed)
    assert unpacked.name == "Haircut ($20)"


def test_date_cb_round_trip():
    packed = DateCb(date="2026-08-01").pack()
    unpacked = DateCb.unpack(packed)
    assert unpacked.date == "2026-08-01"


def test_time_cb_round_trip():
    packed = TimeCb(time="10-00 AM").pack()
    unpacked = TimeCb.unpack(packed)
    assert unpacked.time == "10-00 AM"


def test_different_callback_types_have_distinct_prefixes():
    service_packed = ServiceCb(name="x").pack()
    date_packed = DateCb(date="x").pack()
    assert service_packed != date_packed
    assert service_packed.split(":")[0] != date_packed.split(":")[0]
