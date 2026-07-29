# Appointment Booking Telegram Bot

A Telegram bot for scheduling salon appointments with real-time slot validation, local SQLite persistence, Google Sheets synchronization, and Redis FSM storage.

## Demo

User selects a service -> chooses a date and time -> enters a phone number -> the booking is saved to the local database and synced to Google Sheets.

![Demo](docs/demo.apng)

## Architecture & Design

- **FSM Storage (Redis):** User states and form data are stored in Redis (`RedisStorage`), persisting across bot restarts.
- **Local Persistence (Outbox Pattern):** Bookings are written to a local SQLite database first to prevent data loss.
- **Google Sheets Sync:** Bookings are synced to Google Sheets asynchronously. Failed API calls retry via exponential backoff (`tenacity`) and are reconciled by a background task.
- **Race Condition Prevention:** Time slot conflicts are guarded by SQLite `UNIQUE(date, time)` constraints.
- **Rate Limiting:** `ThrottlingMiddleware` uses `cachetools.TTLCache` to bound memory usage while preventing spam.

## Tech Stack

- Python 3.14+
- uv (Package Manager)
- aiogram 3.x
- Redis (`redis-py`)
- SQLite (`aiosqlite`)
- Google Sheets API (`gspread-asyncio`)
- taskipy

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/dar-key/appointment-booking-bot.git
   cd appointment-booking-bot
   ```

````

2. Install dependencies:

   ```bash
   uv sync
   ```

3. Copy the environment template and set your values:

   ```bash
   cp .env.example .env
   ```

4. Place your Google Service Account credentials file (`credentials.json`) in the project root.

5. Start the bot:

   ```bash
   uv run task start
   ```

## Google Sheets Setup

1. Open Google Cloud Console and create a project.
2. Enable the Google Sheets API and Google Drive API.
3. Create a Service Account, generate a JSON key, and download it to the root directory as `credentials.json`.
4. Share your target Google Sheet with the Service Account email (Editor permissions).
5. Copy the Spreadsheet ID into `.env` (`GOOGLE_SHEET_ID`).

## Docker Deployment

Start the bot and Redis containers using Docker Compose:

```bash
# Build and start services in background
docker compose up -d --build

# View logs
docker compose logs -f bot

# Stop services
docker compose down
```

`credentials.json` is mounted read-only at runtime via `docker-compose.yml` to prevent baking secrets into the image.

## Testing and Quality

```bash
# Run test suite
uv run pytest

# Run linter
uv run ruff check .
```
````
