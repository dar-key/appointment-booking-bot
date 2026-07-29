# Appointment Booking Telegram Bot

A Telegram bot for booking appointments with Google Sheets as the backend.

The bot guides users through the booking process, checks time slot availability, and stores reservations in a shared Google Spreadsheet.

> **Demo Bot**
>
> https://t.me/booking_temp_bot

---

**Demo**

User selects a service -> chooses a date and time -> enters a phone number -> the booking instantly appears in Google Sheets.

![Demo](docs/demo.apng)

---

## Features

- Step-by-step booking flow
- Google Sheets integration
- Prevents double bookings
- Checks available time slots before confirmation
- Asynchronous request handling
- Multi-user support

---

## Tech Stack

- Python 3.11+
- aiogram 3
- gspread
- Google Sheets API
- aiosqlite
- python-dotenv

---

## Installation

1. Clone the repository.

   ```bash
   git clone https://github.com/dar-key/appointment-booking-bot.git
   cd appointment-booking-bot
   ```

2. Install the dependencies.

   ```bash
   uv sync
   ```

3. Copy the environment template to a new `.env` file and add your variables:

   ```bash
   cp .env.example .env
   ```

4. Run the bot.

   ```bash
   uv run task start
   ```

---

## Google Sheets Setup

1. Create a project in Google Cloud Console.
2. Enable the **Google Sheets API** and **Google Drive API**.
3. Create a Service Account and download its JSON credentials.
4. Rename the file to `credentials.json`.
5. Share your spreadsheet with the Service Account email.
6. Copy the spreadsheet ID into your `.env` file.

---

## Configuration

Place your Google service account credentials (json) in the project root.

Insert your Telegram bot token, Google Sheet ID and Google credentials file name in the `.env.example`. Rename it to `.env`
