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

- Python 3.10
- uv (Package Manager)
- aiogram 3.x
- Redis (`redis-py`)
- SQLite (`aiosqlite`)
- Google Sheets API (`gspread-asyncio`)
- taskipy

## Installation

### Prerequisites

- Python 3.10+ (managed via `uv`)
- Redis Server (for local development)

### 1. Project Setup

```bash
# Clone the repository
git clone https://github.com/dar-key/appointment-booking-bot.git
cd appointment-booking-bot

# Install dependencies
uv sync

# Copy the environment template and set your values
cp .env.example .env
```

### 2. Google Sheets Setup

1. Open the Google Cloud Console and create a project.
2. Enable the Google Sheets API and Google Drive API.
3. Create a Service Account, generate a JSON key, and download it to the project root directory as `credentials.json`.
4. Share your target Google Sheet with the Service Account email (Editor permissions).
5. Copy the Spreadsheet ID into your `.env` file (`GOOGLE_SHEET_ID`).

---

## Running the Application

### Option 1: Local setup (without Docker)

1. **Start Redis via Docker:**

   ```bash
   docker run -d --name bot-redis -p 6379:6379 redis:alpine
   ```

   _(Note: Ensure your `.env` file points to `localhost:6379` for the Redis connection)._

2. **Start the bot:**
   ```bash
   uv run task start
   ```

_(Alternative: If you have Redis installed natively on your OS, ensure the service is running via `sudo systemctl start redis` or `brew services start redis` before running the bot)._

### Option 2: Docker Deployment

```bash
# Build and start
docker compose up -d --build

# View logs
docker compose logs -f bot

# Stop
docker compose down
```

---

## Google Sheets Setup

1. Open Google Cloud Console and create a project.
2. Enable the Google Sheets API and Google Drive API.
3. Create a Service Account, generate a JSON key, and download it to the root directory as `credentials.json`.
4. Share your target Google Sheet with the Service Account email (Editor permissions).
5. Copy the Spreadsheet ID into `.env` (`GOOGLE_SHEET_ID`).

## Testing

```bash
# Run test suite
uv run pytest

# Run linter
uv run ruff check .
```
