import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def fetch_psx_data(symbol: str):
    try:
        url = f"https://dps.psx.com.pk/times/1"  # Live tickers feed from PSX
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Search for symbol in the ticker list
            for item in data:
                if item.get("code", "").upper() == symbol.upper():
                    return item
        
        # Backup API attempt
        url_alt = f"https://dps.psx.com.pk/stock/{symbol.upper()}"
        res_alt = requests.get(url_alt, headers=headers, timeout=10)
        if res_alt.status_code == 200:
            return res_alt.json()
            
        return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    
    # Financial Filter
    financial_keywords = [
        "sys", "ogdc", "ffc", "hubc", "luck", "cnergy", "ubl", "mebl",
        "stock", "psx", "market", "price", "share", "dividend", "trading", 
        "crypto", "forex", "gold", "xauusd"
    ]
    
    is_financial = any(kw in user_text.lower() for kw in financial_keywords) or len(user_text) <= 6
    
    if not is_financial and not user_text.startswith("/"):
        await update.message.reply_text(
            "❌ Sorry, I am strictly a financial and PSX market assistant."
        )
        return

    symbol = user_text.upper().replace("TELL ME ABOUT ", "").strip()
    await update.message.reply_text(f"🔍 Fetching live data for {symbol} from PSX...")
    
    data = fetch_psx_data(symbol)
    
    if data:
        # Extract fields safely
        code = data.get("code", symbol)
        price = data.get("price") or data.get("current") or "N/A"
        change = data.get("change") or "0.00"
        volume = data.get("volume") or "N/A"
        
        response_msg = (
            f"📊 *PSX Stock Report: {code}*\n\n"
            f"💰 *Price:* PKR {price}\n"
            f"📈 *Change:* {change}\n"
            f"🔄 *Volume:* {volume}\n\n"
            f"✅ *Source:* Official PSX Data Feed"
        )
    else:
        response_msg = f"⚠️ Symbol `{symbol}` not found or API limits reached. Please verify ticker symbol (e.g., OGDC, SYS, CNERGY)."
        
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
