import requests
import json
import schedule
import time
import itertools
from colorama import init, Fore, Style
import os
import sys
import traceback

# Initialize Colorama for Windows
init()

# Load configuration from config.json
def load_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config

config = load_config()

# URLs for Discord webhooks
GENERAL_DISCORD_WEBHOOK_URL = config['general_webhook_url']
PRICE_ERROR_DISCORD_WEBHOOK_URL = config['price_error_webhook_url']

# List of categories to monitor with the number of products to check
categories = config['categories']

# List of Amazon domains to monitor
domains = config['domains']

# Check interval in seconds (5 seconds instead of 5 minutes)
check_interval_seconds = config.get('check_interval_seconds', 5)

# Discount threshold percentage
discount_threshold = config.get('discount_threshold', 70)

# Option to switch to the next API key when one is exhausted
use_next_api_on_exhaustion = config.get('use_next_api_on_exhaustion', 'no').lower() == 'yes'

# Load API keys from api.txt
def load_api_keys():
    with open('api.txt', 'r') as f:
        api_keys = [line.strip() for line in f if line.strip()]
    return api_keys

api_keys = load_api_keys()

# Create a cyclic iterator to alternate between API keys
api_key_iterator = itertools.cycle(api_keys)

BLUE = '\033[94m'
ENDC = '\033[0m'

# Define the text to print
text = (
    "                   _                            _ _             \n"
    "                 | |                          (_) |            \n"
    "   __ ___  ____ _| | __  _ __ ___   ___  _ __  _| |_ ___  _ __ \n"
    "  / _` \\ \\/ / _` | |/ / | '_ ` _ \\ / _ \\| '_ \\| | __/ _ \\| '__|\n"
    " | (_| |>  < (_| |   <  | | | | | | (_) | | | | | || (_) | |   \n"
    "  \\__, /_/\\_\\__, |_|\\_\\ |_| |_| |_|\\___/|_| |_|_|\\__\\___/|_|   \n"
    "   __/ |       | |                                             \n"
    "  |___/        |_|                                             \n"
)

# Print the text in blue
print(BLUE + text + ENDC)

# Function to get the next API key
def get_next_api_key():
    return next(api_key_iterator)

# Verify the validity of API keys
def verify_api_keys():
    valid_keys = []
    invalid_keys = []
    for key in api_keys:
        response = requests.get(f'https://api.keepa.com/token/?key={key}')
        if response.status_code == 200:
            valid_keys.append(key)
            print(Fore.GREEN + f"API key {key} is valid." + Style.RESET_ALL)
        else:
            invalid_keys.append(key)
            print(Fore.RED + f"API key {key} is invalid or has reached its limit." + Style.RESET_ALL)
    return valid_keys, invalid_keys

# Verify API keys at startup
valid_api_keys, invalid_api_keys = verify_api_keys()

# Inform if no valid API keys are available
if not valid_api_keys:
    print(Fore.RED + "No valid API keys are available." + Style.RESET_ALL)
else:
    print(Fore.GREEN + "Active API keys: " + ', '.join(valid_api_keys) + Style.RESET_ALL)

# Verify the validity of the general Discord webhook
def verify_general_discord_webhook():
    if GENERAL_DISCORD_WEBHOOK_URL:
        headers = {"Content-Type": "application/json"}
        data = {"content": "The general webhook is operational."}
        response = requests.post(GENERAL_DISCORD_WEBHOOK_URL, json=data, headers=headers)
        if response.status_code == 204:
            print(Fore.GREEN + "General Discord webhook is valid." + Style.RESET_ALL)
        else:
            print(Fore.RED + f"Failed to validate general Discord webhook: {response.status_code}." + Style.RESET_ALL)
    else:
        print(Fore.RED + "General webhook not defined in config.json." + Style.RESET_ALL)

verify_general_discord_webhook()

# Verify the validity of the price error Discord webhook
def verify_price_error_discord_webhook():
    if PRICE_ERROR_DISCORD_WEBHOOK_URL:
        headers = {"Content-Type": "application/json"}
        data = {"content": "The price error webhook is operational."}
        response = requests.post(PRICE_ERROR_DISCORD_WEBHOOK_URL, json=data, headers=headers)
        if response.status_code == 204:
            print(Fore.GREEN + "Price error Discord webhook is valid." + Style.RESET_ALL)
        else:
            print(Fore.RED + f"Failed to validate price error Discord webhook: {response.status_code}." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Price error webhook not defined in config.json." + Style.RESET_ALL)

verify_price_error_discord_webhook()

# Function to send a message to a Discord webhook
def send_to_discord(webhook_url, embed):
    headers = {"Content-Type": "application/json"}
    data = {"embeds": [embed]}
    response = requests.post(webhook_url, json=data, headers=headers)
    if response.status_code == 204:
        print("Message successfully sent to webhook.")
    else:
        print(f"Failed to send message to webhook: {response.status_code}")

# Function to send a general error message to the general webhook
def send_general_error_message(message):
    if GENERAL_DISCORD_WEBHOOK_URL:
        embed = {
            "title": "Saturn Monitor Error",
            "description": message,
            "color": 0xFF0000  # Red
        }
        send_to_discord(GENERAL_DISCORD_WEBHOOK_URL, embed)
    else:
        print(Fore.RED + "General webhook not defined in config.json, cannot send error message." + Style.RESET_ALL)

# Function to send a price error message to the dedicated webhook
def send_price_error_message(product_title, current_price, discount_percentage, asin, domain):
    if PRICE_ERROR_DISCORD_WEBHOOK_URL:
        embed = {
            "title": product_title,
            "url": f'https://www.amazon.{domain}/dp/{asin}',
            "description": f'Price error detected: {current_price}€ (Discount of {discount_percentage:.2f}%)',
            "thumbnail": {
                "url": f'https://images-na.ssl-images-amazon.com/images/I/{asin}.jpg'
            },
            "image": {
                "url": f'https://graph.keepa.com/pricehistory.png?asin={asin}&domain={domain}'
            },
            "color": 0xFF69B4  # Pink
        }
        send_to_discord(PRICE_ERROR_DISCORD_WEBHOOK_URL, embed)
    else:
        print(Fore.RED + "Price error webhook not defined in config.json, cannot send price error message." + Style.RESET_ALL)

# Function to retrieve ASINs in a specific category and domain
def get_asins_from_category(category_data, domain):
    category_id = category_data['id']
    number_of_products = category_data['number_of_products']
    
    asins = []
    page = 0

    while len(asins) < number_of_products:
        api_key = get_next_api_key()
        response = requests.get(f'https://api.keepa.com/search/?key={api_key}&domain={domain}&category={category_id}&sort=-avg&range=30&page={page}')
        if response.status_code == 200:
            data = response.json()
            new_asins = [product['asin'] for product in data['products']]
            if not new_asins:
                break
            asins.extend(new_asins)
            page += 1
        else:
            print(f"Error retrieving ASINs for category {category_id} with key {api_key} on domain {domain}: {response.status_code}")
            break

    return asins[:number_of_products]

# Function to check prices for a specific domain
def check_prices(asins, domain):
    for asin in asins:
        api_key = get_next_api_key()
        response = requests.get(f'https://api.keepa.com/product?key={api_key}&domain={domain}&asin={asin}')
        if response.status_code == 200:
            data = response.json()
            product = data['products'][0]
            price_history = product['data']['NEW']
            
            # Retrieve current price and highest price
            if price_history:
                current_price = price_history[-1] / 100.0
                highest_price = max(price_history) / 100.0
                
                # Calculate discount percentage
                if highest_price > 0:
                    discount_percentage = ((highest_price - current_price) / highest_price) * 100
                else:
                    discount_percentage = 0.0
                
                # Check if the discount is greater than or equal to the threshold defined in config.json
                if discount_percentage >= discount_threshold:
                    product_title = product['title']
                    send_price_error_message(product_title, current_price, discount_percentage, asin, domain)
            else:
                print(f"No price data available for ASIN {asin} on domain {domain}")
        else:
            print(f"Error retrieving product data for ASIN {asin} with key {api_key} on domain {domain}: {response.status_code}")

# Schedule tasks for each specified category and domain
for domain_code, domain_name in domains.items():
    for category_data in categories:
        asins = get_asins_from_category(category_data, domain_code)
        schedule.every(check_interval_seconds).seconds.do(check_prices, asins=asins, domain=domain_code)

# Send a message to the webhook on initial script startup
def send_startup_message():
    if GENERAL_DISCORD_WEBHOOK_URL:
        embed = {
            "title": "Saturn Monitor Started",
            "description": f"The Saturn Monitor software has successfully started. Monitored Amazon domains: {', '.join(domains.keys())}",
            "color": 0x00FF00,  # Green
            "fields": [
                {"name": "API Status", "value": "🟢" if valid_api_keys else "🔴", "inline": True},
                {"name": "Webhook Status", "value": "🟢" if GENERAL_DISCORD_WEBHOOK_URL else "🔴", "inline": True}
            ],
            "footer": {
                "text": "Saturn Monitor developed by GXQK"
            }
        }
        
        send_to_discord(GENERAL_DISCORD_WEBHOOK_URL, embed)
    else:
        print(Fore.RED + "General webhook not defined in config.json, cannot send startup message." + Style.RESET_ALL)

send_startup_message()

# Main execution loop
while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as e:
        print(Fore.RED + "Unhandled error detected:", e)
        traceback.print_exc()
        time.sleep(60)  # Wait before restarting the script in case of an error
        continue
