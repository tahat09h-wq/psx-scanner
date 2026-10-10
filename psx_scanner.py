import os
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_alert(message_text):
    """Utility to send alerts to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "HTML"
    }
    try:
        res = requests.post(url, data=payload)
        if res.status_code == 200:
            print("✅ Telegram alert delivered successfully!")
        else:
            print(f"❌ Telegram API Error: {res.text}")
    except Exception as e:
        print(f"⚠️ Network Error: {e}")

def run_scanner():
    print("🚀 Running GridPulse PSX Scanner...")
    
    # 1. Immediate Test Ping to verify Telegram Bot Connection
    test_msg = (
        "🤖 <b>GridPulse PSX Scanner Status: ACTIVE</b>\n\n"
        "✅ Cloud connectivity working perfectly!\n"
        "📊 System will auto-scan live market on Monday."
    )
    send_telegram_alert(test_msg)

    # 2. Market Scan Logic
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://dps.psx.com.pk/"
    }
    
    try:
        url = "https://dps.psx.com.pk/times/all"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PSX Connected! Fetched {len(data)} stocks.")
            
            alerts_count = 0
            for stock in data:
                try:
                    symbol = stock.get("symbol", "")
                    current_price = float(stock.get("current", 0) or 0)
                    change_percent = float(stock.get("percent", 0) or 0)
                    volume = int(stock.get("volume", 0) or 0)
                    
                    # Volume Breakout Strategy Rules
                    if current_price >= 5 and volume >= 500000 and change_percent >= 2.0:
                        target_price = current_price * 1.06
                        alert_msg = (
                            f"🚨 <b>VOLUME BREAKOUT ALERT</b> 🚨\n\n"
                            f"📌 <b>Stock:</b> #{symbol}\n"
                            f"💰 <b>Price:</b> PKR {current_price:.2f}\n"
                            f"📈 <b>Change:</b> {change_percent:+.2f}%\n"
                            f"📊 <b>Volume:</b> {volume:,}\n"
                            f"🎯 <b>Target (6%):</b> PKR {target_price:.2f}\n\n"
                            f"⚡ <i>GridPulse AI</i>"
                        )
                        send_telegram_alert(alert_msg)
                        alerts_count += 1
                except Exception:
                    continue
            print(f"Scan complete. Live market alerts triggered: {alerts_count}")
        else:
            print(f"PSX API Response Error: {response.status_code}")
    except Exception as e:
        print(f"Scanner Connection Error: {e}")

if __name__ == "__main__":
    run_scanner()
    
