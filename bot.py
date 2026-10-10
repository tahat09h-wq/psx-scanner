import os
import requests
import time

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

def get_psx_data(symbol):
    """Fetch live data from PSX official portal for a specific stock"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://dps.psx.com.pk/"
    }
    try:
        url = "https://dps.psx.com.pk/times/all"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            for stock in data:
                if stock.get("symbol", "").upper() == symbol.upper():
                    return stock
    except Exception as e:
        print(f"API Error: {e}")
    return None

def send_message(chat_id, text):
    """Send reply back to Telegram user"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram Error: {e}")

def run_bot():
    print("🤖 GridPulse Interactive Community Bot Started...")
    offset = 0
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={offset}&timeout=30"
            response = requests.get(url)
            
            if response.status_code == 200:
                result = response.json()
                for update in result.get("result", []):
                    offset = update["update_id"] + 1
                    message = update.get("message", {})
                    chat_id = message.get("chat", {}).get(id)
                    text = message.get("text", "").strip()
                    
                    if not chat_id or not text:
                        continue
                        
                    # Clean the user input to match stock symbol format
                    query_symbol = text.replace("/", "").strip().upper()
                    
                    # Fetch stock info from PSX
                    stock_data = get_psx_data(query_symbol)
                    
                    if stock_data:
                        symbol = stock_data.get("symbol")
                        current_price = float(stock_data.get("current", 0) or 0)
                        change = float(stock_data.get("change", 0) or 0)
                        percent = float(stock_data.get("percent", 0) or 0)
                        volume = int(stock_data.get("volume", 0) or 0)
                        
                        reply = (
                            f"📊 <b>PSX STOCK REPORT</b>\n\n"
                            f"📌 <b>Stock:</b> #{symbol}\n"
                            f"💰 <b>Current Price:</b> PKR {current_price:.2f}\n"
                            f"📈 <b>Change:</b> {percent:+.2f}% ({change:+.2f})\n"
                            f"📊 <b>Volume:</b> {volume:,}\n\n"
                            f"⚡ <i>GridPulse Community Bot</i>"
                        )
                        send_message(chat_id, reply)
                    else:
                        # Scope Filter: Check if query is financial or general chat
                        financial_keywords = ["PSX", "STOCK", "SHARE", "MARKET", "SYS", "OGDC", "UBL", "HBL", "LUCK", "ENGRO", "TRG", "PRL", "FFC", "MEEZAN"]
                        is_financial = any(kw in text.upper() for kw in financial_keywords)
                        
                        if is_financial or len(text.split()) == 1:
                            send_message(chat_id, f"❌ '{text}' ke naam se koi active PSX stock nahi mila. Sahi symbol bhejiye (misal ke tor par: <code>SYS</code>, <code>OGDC</code>, <code>UBL</code>).")
                        else:
                            send_message(chat_id, "🤖 Main sirf Pakistan Stock Exchange (PSX) aur financial markets ke baray mein maloomat de sakta hoon. Kisi stock ka symbol bhej kar uski details poochein!")
                            
        except Exception as e:
            print(f"Polling Error: {e}")
            
        time.sleep(2)

if __name__ == "__main__":
    run_bot()
