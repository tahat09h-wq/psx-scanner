import os
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_alert(symbol, price, change_percent):
    message = (
        f"🚨 *PSX SCANNER ALERT* 🚨\n\n"
        f"📌 *Stock:* `#{symbol}`\n"
        f"💰 *Current Price:* PKR {price}\n"
        f"📈 *Change:* {change_percent}%\n\n"
        f"⚡ _GridPulse AI Scanner_"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=payload)
        print(f"Alert sent for #{symbol}")
    except Exception as e:
        print(f"Error: {e}")

def run_scanner():
    print("Scanning PSX Official Portal...")
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://dps.psx.com.pk/"
    }
    try:
        response = requests.get("https://dps.psx.com.pk/times/all", headers=headers)
        if response.status_code == 200:
            print("Data fetched successfully from PSX!")
        else:
            print("Failed to fetch data.")
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    run_scanner()
