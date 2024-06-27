# Keepa Monitor

Keepa Monitor is a Python script designed to monitor product prices on Amazon using the Keepa API. It sends notifications via Discord webhooks for price errors and system statuses.

## Features

- **Price Monitoring**: Monitors product prices on specified Amazon domains.
- **Discord Integration**: Sends notifications to Discord webhooks for price errors and system statuses.
- **Flexible Configuration**: Easily configurable via `config.json` for API keys, webhook URLs, categories, and check intervals.
- **Error Handling**: Handles API key exhaustion and system crashes gracefully, with automated recovery.

## Requirements

- Python 3.x
- `requests`, `schedule`, and `colorama` Python packages.

## Installation

1. **Clone the repository:**

   ```bash
   git clone <repository_url>
   cd keepa-monitor
