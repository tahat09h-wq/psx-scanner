import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def fetch_psx_data(symbol: str):
  try:
    response = requests.get(
        f"https://dps.psx.com.pk/stock/{symbol.upper()}", timeout=10
    )
    if response.status_code == 200:
      data = response.json()
      if data:
        return data
    return None
  except Exception:
    return None


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_text = update.message.text.strip()

  # Financial & Stock Market Filter
  financial_keywords = [
      "sys",
      "ogdc",
      "ffc",
      "hubc",
      "luck",
      "stock",
      "psx",
      "market",
      "price",
      "share",
      "dividend",
      "trading",
      "crypto",
      "forex",
      "gold",
      "xauusd",
  ]
  is_financial = any(kw in user_text.lower() for kw in financial_keywords)

  if not is_financial and not user_text.startswith("/"):
    await update.message.reply_text(
        "❌ Sorry, I am strictly a financial and PSX market assistant. I can"
        " only provide stock market reports, financial data, and trading"
        " insights."
    )
    return

  symbol = user_text.upper()
  await update.message.reply_text(
      f"🔍 Fetching live data for {symbol} from PSX..."
  )

  data = fetch_psx_data(symbol)
  if data:
    response_msg = (
        f"📊 *PSX Market Report: {symbol}*\n\n✅ Data successfully fetched from"
        " official PSX API feed."
    )
  else:
    response_msg = (
        f"⚠️ Symbol `{symbol}` not found or market data currently unavailable."
    )

  await update.message.reply_text(response_msg, parse_mode="Markdown")


def main():
  if not TELEGRAM_BOT_TOKEN:
    print("Error: TELEGRAM_BOT_TOKEN is missing!")
    return

  app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
  app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

  print("🤖 GridPulse Unified Bot Started...")
  app.run_polling()


if __name__ == "__main__":
  main()
