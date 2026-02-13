# Polymarket BTC 5-Minute Trading Bot

A trading bot for Polymarket BTC 5-minute up/down markets.

## Features

- Generate market slugs from timestamps
- Find active BTC 5-minute up/down markets
- Automatically detect current market window

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the bot:
```bash
python main.py
```

## Usage

The bot generates slugs in the format: `btc-updown-5m-{timestamp}`

Example:
- Current timestamp: 1770885600
- Generated slug: `btc-updown-5m-1770885600`

## API Endpoints

The bot uses Polymarket's public API:
- Base URL: `https://clob.polymarket.com`
- Markets endpoint: `https://clob.polymarket.com/markets/{slug}`

## Notes

- Markets are 5-minute intervals, so timestamps are rounded down to the nearest 5-minute mark
- The bot tries both the current and previous 5-minute window to find active markets

