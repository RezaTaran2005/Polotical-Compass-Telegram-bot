# 🧭 Political Compass Telegram Bot

A professional, modular Telegram bot that runs the Political Compass test.

---

## Project Structure

```
political_compass_bot/
├── bot.py                   # Entry point — starts polling
├── config.py                # All configuration constants
├── requirements.txt
├── questions.json           # Question bank (edit freely, no code changes needed)
├── .env.example             # Environment variable template
│
├── handlers/
│   ├── __init__.py
│   ├── start.py             # /start command + membership gate
│   └── quiz.py              # Full quiz flow (answers, navigation, results)
│
├── keyboards/
│   ├── __init__.py
│   └── inline.py            # All InlineKeyboardMarkup builders
│
├── services/
│   ├── __init__.py
│   ├── membership.py        # Channel membership check via Telegram API
│   ├── question_loader.py   # JSON question loader with validation & caching
│   ├── scoring.py           # Score calculation and normalisation logic
│   └── chart.py             # Matplotlib Political Compass image generator
│
└── utils/
    ├── __init__.py
    └── user_state.py        # In-memory per-user session storage
```

---

## Quick Start

### 1. Clone and install dependencies

```bash
git clone https://github.com/RezaTaran2005/Polotical-Compass-Telegram-bot.git
cd political_compass_bot
pip install -r requirements.txt
```

### 2. Configure the bot

```bash
cp .env.example .env
# Edit .env and set BOT_TOKEN and REQUIRED_CHANNEL_ID
```

> **How to find your channel's numeric ID:**
> Forward any message from your channel to [@username_to_id_bot](https://t.me/username_to_id_bot).
> It will look like `-1001234567890`.

### 3. Make the bot an admin of your channel

The bot **must** have at least the "Read Messages" admin right on the channel so it can call `get_chat_member()` for membership checks.

### 4. Run

```bash
python bot.py
```

---

## Customising Questions

Edit **`questions.json`** — no Python changes required.

Each question object has:

| Field       | Type     | Description                          |
|-------------|----------|--------------------------------------|
| `id`        | int      | Unique identifier                    |
| `text`      | string   | The statement shown to the user      |
| `axis`      | `"x"` or `"y"` | Economic (`x`) or Social (`y`) axis |
| `units`     | int > 0  | Question weight                      |
| `direction` | `1` or `-1` | `1` = agree pushes right/auth; `-1` = agree pushes left/lib |

You can **add, remove, reorder, or reweight** questions by editing the JSON file and restarting the bot.

---

## Score Calculation

For each answer:

```
contribution = answer_value × units × direction
```

Answer values:
- Strongly Agree → `+2`
- Agree → `+1`
- Disagree → `-1`
- Strongly Disagree → `-2`

Raw X and Y totals are then normalised independently to **[-10, +10]** using each axis's maximum possible score.

---

## Political Quadrants

| X     | Y     | Position              |
|-------|-------|-----------------------|
| ≥ 0   | ≥ 0   | Right Authoritarian   |
| < 0   | ≥ 0   | Left Authoritarian    |
| ≥ 0   | < 0   | Right Libertarian     |
| < 0   | < 0   | Left Libertarian      |

---

## Requirements

- Python 3.12+
- `aiogram==3.13.1`
- `matplotlib==3.9.2`
- `aiofiles==23.2.1`
