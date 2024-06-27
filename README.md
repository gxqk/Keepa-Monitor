Keepa Monitor
Keepa Monitor is a Python script designed to monitor product prices on Amazon using the Keepa API. It checks for price drops and sends notifications via Discord webhooks.

Features
Price Monitoring: Monitors product prices on specified Amazon domains (e.g., amazon.com, amazon.co.uk) using Keepa API.
Notification System: Sends notifications to Discord webhooks for price errors and system statuses.
Flexible Configuration: Configurable via config.json for API keys, webhook URLs, categories, and check intervals.
Error Handling: Handles API key exhaustion and system crashes gracefully, with automated recovery.
Requirements
Python 3.x
Required Python packages: requests, schedule, colorama (Install via pip install -r requirements.txt)
Installation
Clone the repository:

bash
Copier le code
git clone <repository_url>
cd keepa-monitor
Install dependencies:

bash
Copier le code
pip install -r requirements.txt
Configure config.json:

Rename config.example.json to config.json.
Fill in your Discord webhook URLs (general_webhook_url, price_error_webhook_url).
Add your Amazon categories (categories) and domains (domains).
Set the check interval (check_interval_minutes) and other settings.
Run the script:

bash
Copier le code
python main.py
Configuration (config.json)
Example config.json structure:

json
Copier le code
{
  "general_webhook_url": "https://discord.com/api/webhooks/...",
  "price_error_webhook_url": "https://discord.com/api/webhooks/...",
  "categories": [
    {
      "id": 281052,
      "number_of_products": 50
    },
    {
      "id": 67263031,
      "number_of_products": 100
    }
  ],
  "domains": {
    "com": 1,
    "de": 3,
    "co.uk": 5
  },
  "check_interval_minutes": 5,
  "use_next_api_on_exhaustion": true
}
Contributing
Contributions are welcome! If you have suggestions, enhancements, or issues, please submit them via GitHub issues or fork the repository and submit a pull request.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Credits
Developed by Your Name
Inspired by Keepa API and Discord webhooks.
Adjust the placeholders (<repository_url>, Your Name, yourusername) with your actual repository URL and your GitHub username or organization.

Feel free to enhance this README.md further with more detailed usage examples, troubleshooting tips, or any other relevant information specific to your project's requirements.
