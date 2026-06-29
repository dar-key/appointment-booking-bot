## [Ссылка для теста бота](https://t.me/gspread_booking_bot)

# Telegram-бот для онлайн-записи (aiogram 3 + Google Sheets)

Простой асинхронный бот для записи клиентов на услуги салона. Бот собирает данные пользователя по шагам (FSM), проверяет занятость слотов и записывает бронирования в Google Таблицу.

## Основной функционал

- Пошаговый сценарий бронирования (выбор услуги -> выбор даты -> выбор времени -> ввод телефона).
- Асинхронная запись в Google Sheets без блокировки основного потока бота.
- Защита от параллельной записи на одно и то же время (Race Condition).
- Проверка занятых слотов перед выводом клавиатуры пользователю.

## Системные требования

- Python 3.11 или выше
- Сервисный аккаунт Google Cloud (с доступом к Sheets и Drive API)

## Установка и запуск

1. Клонируйте репозиторий:

```bash
git clone https://github.com/dar-key/service-booking-bot.git
cd service-booking-bot
```

2.  Создайте и активируйте виртуальное окружение:

```bash
python -m venv .venv
source .venv/bin/activate  # Для Linux/macOS
.venv\Scripts\activate     # Для Windows
```

3.  Установите зависимости:

```bash
pip install -r requirements.txt
```

4.  Подготовьте файл конфигурации .env в корне проекта:

```bash
BOT_TOKEN=123456:ABC-DEF_your_token_here
SPREADSHEET_ID=your_google_sheet_id_here
```

5.  Положите файл ключа сервисного аккаунта Google под именем credentials.json в
    корневую директорию проекта.

6.  Запустите бота:

```bash
python booking_bot.py
```

Настройка интеграции с Google Sheets

1.  Создайте проект в Google Cloud Console и включите Sheets API и Drive API.
2.  Создайте Сервисный аккаунт, скачайте его ключ в формате JSON и переименуйте
    в credentials.json.
3.  Создайте Google Таблицу и добавьте доступ на редактирование (кнопка
    "Поделиться") для email-адреса сервисного аккаунта.
4.  Скопируйте ID таблицы из адресной строки и укажите его в .env.
