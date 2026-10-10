import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def fetch_psx_market_data(symbol: str):
    symbol = symbol.strip().upper()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*'
    }
    
    # Official PSX list/times feed endpoints containing all market tickers simultaneously
    endpoints = [
        "https://dps.psx.com.pk/times/1",
        "https://dps.psx.com.pk/live/list",
        "https://dps.psx.com.pk/symbols"
    ]
    
    for url in endpoints:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                items = data.get("data", data) if isinstance(data, dict) else data
                
                if isinstance(items, list):
                    for item in items:
                        item_symbol = str(item.get("symbol") or item.get("code") or item.get("ticker") or "").upper()
                        if symbol == item_symbol:
                            return item
                elif isinstance(items, dict):
                    if symbol in items:
                        return items[symbol]
        except Exception as e:
            print(f"Endpoint error ({url}): {e}")
            
    # Fallback lookup directly via stock summary
    try:
        url = f"https://dps.psx.com.pk/stock/{symbol}"
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass

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
    await update.message.reply_text(f"🔍 Fetching live data for {symbol}...")
    
    data = fetch_psx_market_data(symbol)
    
    if data:
        stats = data.get("stats", {}) if isinstance(data.get("stats"), dict) else {}
        code = data.get("symbol") or data.get("code") or stats.get("symbol") or symbol
        price = data.get("current") or stats.get("current") or data.get("price") or stats.get("price") or "N/A"
        change = data.get("change") or stats.get("change") or "0.00"
        volume = data.get("volume") or stats.get("volume") or "N/A"
        
        response_msg = (
            f"📊 *PSX Market Report: {code}*\n\n"
            f"💰 *Current Price:* PKR {price}\n"
            f"📈 *Change:* {change}\n"
            f"🔄 *Volume:* {volume}\n\n"
            f"✅ *Source:* PSX Direct Feed"
        )
    else:
        response_msg = (
            f"⚠️ Symbol `{symbol}` data unavailable.\n"
            f"Make sure to use correct ticker symbols like `OGDC`, `SYS`, `KEL`, `FFC`."
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
