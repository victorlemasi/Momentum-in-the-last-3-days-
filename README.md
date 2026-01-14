# Momentum Trading Bot

A Python-based trading bot that calculates momentum using Yahoo Finance data and places trades via MetaTrader 5 (MT5).

## Features
- **Momentum Calculation**: Uses `yfinance` to fetch historical data and calculate momentum over a 3-day period.
- **MT5 Integration**: Automatically places buy/sell orders based on momentum signals.
- **Environment Driven**: Sensitive credentials are managed via a `.env` file.
- **Safe Trading**: Orders are placed without predefined Take Profit (TP) or Stop Loss (SL) as per current configuration.

## Setup

### 1. Prerequisites
Ensure you have Python 3.8+ installed and a MetaTrader 5 account.

### 2. Installation
Clone the repository and install the dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory (you can use `.env.example` as a template):
```env
BROKER_LOGIN=your_mt5_account_number
BROKER_PASSWORD=your_mt5_password
BROKER_SERVER=your_broker_server_name
```

### 4. Running the Bot
Run the main script:
```bash
python main.py
```
Follow the prompts to enter symbols (e.g., `EURUSD, GOLD, BTCUSD`) and lot size.

## Project Structure
- `main.py`: The primary trading bot script.
- `Version 1.1.py`: An alternative/older version of the bot.
- `.env`: (Local only) Stores your broker credentials.
- `requirements.txt`: Python package dependencies.
- `.gitignore`: Prevents sensitive files from being committed.

## Disclaimer
Trading involves significant risk. This bot is for educational purposes. Always test on a demo account before using real capital.
