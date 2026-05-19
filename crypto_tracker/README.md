# 🪙 Crypto Portfolio Tracker

A Python desktop app built with Tkinter for tracking cryptocurrency assets.
Final project for Introduction to Programming 2.

---

## Project Structure

```
crypto_tracker/
├── main.py        # Entry point — run this
├── auth.py        # AuthManager class + Login window (Class 3)
├── models.py      # Asset class, Portfolio class, log_action decorator
├── api.py         # CoinGecko live price fetching (no API key needed)
├── charts.py      # Matplotlib pie + bar chart windows
├── app.py         # Main Tkinter dashboard
├── requirements.txt
└── data/          # Auto-created on first run
    ├── users.json       # Hashed user credentials
    ├── portfolio.json   # Per-user portfolio data
    └── log.txt          # Action log (decorator output)
```

---

## Setup

```bash
# 1. Install dependencies (only matplotlib needed)
pip install matplotlib

# 2. Run the app
python main.py
```

---

## Features

| Feature | Description |
|---|---|
| Login / Register | Accounts stored in `data/users.json` (SHA-256 hashed passwords) |
| Add Asset | Enter name, symbol, quantity, and optional price |
| Remove Asset | Select row → click Remove |
| Update Price | Select row → click Update Price → enter new value |
| Fetch Live Prices | Pulls real-time USD prices from CoinGecko API |
| Search | Filter table by name or symbol as you type |
| Pie Chart | Portfolio distribution by USD value |
| Bar Chart | Each asset's total USD value |
| Save / Load | Persist portfolio to/from `data/portfolio.json` |
| Error Handling | messagebox alerts for all invalid inputs |

---

## Supported Live-Price Symbols

BTC, ETH, SOL, BNB, XRP, ADA, DOGE, DOT, MATIC, LTC, AVAX, LINK, UNI, ATOM, TRX, SHIB, TON, BCH, NEAR, APT

(Custom symbols can still be added manually with your own price.)

---

## Course Requirements Covered

| Requirement | Where |
|---|---|
| Clean syntax, variables, I/O | All files |
| Conditionals & loops | `models.py`, `app.py`, `api.py` |
| Lists, dicts, sets, tuples | `Portfolio` uses list + set; `summary()` returns tuple |
| JSON file persistence | `models.py` save/load, `auth.py` users |
| Functions & modules | 5 separate modules |
| OOP — 2+ classes | `Asset`, `Portfolio`, `AuthManager` |
| Exception handling | `try/except` in api, auth, app, models |
| Advanced feature — decorator | `@log_action` in `models.py` |
| Tkinter GUI | `auth.py` (login), `app.py` (dashboard) |
| External API | `api.py` — CoinGecko free API |
| Charts | `charts.py` — matplotlib pie & bar |
