import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def fetch_investify_data(symbol: str):
    symbol = symbol.strip().upper()
    
    # Investify Web/API Headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': f'https://www.investify.pk/stocks/{symbol.lower()}',
        'Accept': 'application/json, text/plain, */*'
    }
    
    # Try searching / fetching via Investify backend endpoints
    endpoints = [
        f"https://www.investify.pk/api/stocks/{symbol}",
        f"https://www.investify.pk/api/search?q={symbol}",
        f"https://www.investify.pk/stocks/{symbol}"
    ]
    
    for url in endpoints:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                if "application/json" in response.headers.get("Content-Type", ""):
                    data = response.json()
                    if data:
                        return data
        except Exception as e:
            print(f"Error fetching from {url}: {e}")
            
    return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    
    financial_keywords = [
        "sys", "ogdc", "ffc", "hubc", "luck", "cnergy", "ubl", "mebl", "kel", 
        "stock", "psx", "market", "price", "share", "dividend", "trading"
    ]
    
    is_financial = any(kw in user_text.lower() for kw in financial_keywords) or len(user_text) <= 6
    
    if not is_financial and not user_text.startswith("/"):
        await update.message.reply_text("❌ Sorry, I am strictly a financial and PSX market assistant.")
        return

    symbol = user_text.upper().strip()
    await update.message.reply_text(f"🔍 Fetching live data for {symbol} from Investify...")
    
    data = fetch_investify_data(symbol)
    
    if data:
        # Extract fields flexibly based on API return schema
        code = data.get("symbol") or data.get("code") or symbol
        price = data.get("current") or data.get("price") or data.get("last_price") or "N/A"
        change = data.get("change") or data.get("price_change") or "0.00"
        volume = data.get("volume") or "N/A"
        
        response_msg = (
            f"📊 *Investify PSX Report: {code}*\n\n"
            f"💰 *Current Price:* PKR {price}\n"
            f"📈 *Change:* {change}\n"
            f"🔄 *Volume:* {volume}\n\n"
            f"✅ *Source:* Investify Live Feed"
        )
    else:
        response_msg = (
            f"⚠️ Symbol `{symbol}` not found on Investify.\n"
            f"Please verify the ticker symbol (e.g., OGDC, SYS, CNERGY, KEL)."
        )
        
    await update.message.reply_text(response_msg, parse_mode="Markdown")

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN missing!")
        return
    
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 GridPulse Bot Active...")
    app.run_polling()

if __name__ == "__main__":
    main()
