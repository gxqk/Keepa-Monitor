
# 🚫 Don't be a skid or reselling this code src, please !!!🚫
# ✅ YOU NEED AN API KEY OF KEEPA.

# Keepa Monitor X GXQK MONITOR

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
   cd Keepa-Monitor-main
   ```
2. **Install Dependicies**

   **Windows**

     - Launch install.bat
   
   **Ubuntu**

   ```bash
   pip install -r requirements.txt
   ```
   
3. **Configure `config.json`:**
- Add your Discord webhook URLs (`general_webhook_url` and `price_error_webhook_url`).
- Define Amazon categories (`categories`) and domains (`domains`).
- Adjust check intervals (`check_interval_seconds`) and other settings as needed.
- Choose in (`use_next_api_on_exhaustion`) yes or no.
- adjust (`discount_threshold`) if u want.

4. **Add your KEEPA API `api.txt`**
- replace " test " by your keepa api

*⚠ALERT : KEEPA API KEY ARE NOT FREE, YOU CAN FIND IT IN https://keepa.com/#!api  ⚠*


4. **Run the script:**

   **Windows**

   - Launch start.bat

   **UBUNTU**

   ```bash
   py main.py
   or
   python3 main.py
   ```

**----------------------------------------------------------------------------------------**

## ISSUES ?

   **Add me on discord : gxqk**

## LICENCE

   **This project is licensed under the MIT License. See the LICENSE file for details.**
   


   
   
   

