from aiogram.filters.callback_data import CallbackData


class ServiceCb(CallbackData, prefix="service"):
    name: str


class DateCb(CallbackData, prefix="date"):
    date: str


class TimeCb(CallbackData, prefix="time"):
    time: str
