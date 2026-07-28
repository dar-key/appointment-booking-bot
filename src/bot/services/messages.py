def booking_confirmation(
    service: str,
    date: str,
    time: str,
    phone: str,
) -> str:

    return (
        f"<b>Booking Confirmed!</b>\n\n"
        f"<b>Your details:</b>\n"
        f"- Service: <code>{service}</code>\n"
        f"- Date: <code>{date}</code>\n"
        f"- Time: <code>{time}</code>\n"
        f"- Phone: <code>{phone}</code>\n\n"
        f"We look forward to seeing you!"
    )
