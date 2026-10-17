import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Keep Render Alive (fake web server)
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(b"Pip Hunters Bot Live")
    def log_message(self, *args): return

def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()
threading.Thread(target=keep_alive, daemon=True).start()

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "https://t.me/PipHuntersSignals1"
DERIV = "https://t.deriv.link?t=N886WMZM3C76"
CONTACT = "@PipHuntersSignals2"

async def start(update, context):
    kb = [
        ["🚀 Get Free Trading Signals", "📢 Join Our Free Channel"],
        ["📈 About Our Forex & Synthetic Signals", "🆘 Get Help & Support"],
        ["📌 Channel Info & Trading Updates", "📩 Contact Our Team"],
        ["📊 Trading Risk Management Tips", "👋 Welcome! Start Here"],
        ["📝 Register with our trusted broker", "🔥 Get vip access now🥺"],
        ["✅ Verify Deriv Registration"]
    ]
    await update.message.reply_text(
        "🔥 **WELCOME TO PIP HUNTERS SIGNALS** 🔥\n\n"
        "We provide 5-10 FREE Forex & Synthetic signals daily with 85% accuracy!\n\n"
        "👇 Choose from menu below:",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True),
        parse_mode="Markdown"
    )

async def handle_all(update, context):
    text = update.message.text.lower()
    
    if "get free trading signals" in text:
        await update.message.reply_text(
            "🔥 **TODAY'S FREE SIGNAL** 🔥\n\n"
            "💰 XAUUSD (GOLD) - BUY\n"
            "📍 Entry: 2650.00\n"
            "🛑 SL: 2640.00\n"
            "🎯 TP1: 2660.00\n"
            "🎯 TP2: 2675.00\n\n"
            "For 10 signals daily, join channel:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ JOIN FREE CHANNEL", url=CHANNEL)]])
        )
    elif "join our free channel" in text:
        await update.message.reply_text(
            f"📢 Join our FREE channel here:\n\n{CHANNEL}\n\nDaily signals + Market news!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 JOIN NOW", url=CHANNEL)]])
        )
    elif "about our forex" in text:
        await update.message.reply_text(
            "📈 **ABOUT OUR SIGNALS**\n\n"
            "✅ Forex Majors: EURUSD, GBPUSD, XAUUSD\n"
            "✅ Synthetics: Boom & Crash, Volatility\n"
            "✅ 5-10 Signals Daily\n"
            "✅ 85% Accuracy\n"
            "✅ Full SL & TP Provided\n"
            "✅ Risk Management Included"
        )
    elif "get help & support" in text:
        await update.message.reply_text(f"🆘 **HELP & SUPPORT**\n\nContact admin: {CONTACT}\nWe reply within 1 hour!\n\nChannel: {CHANNEL}")
    elif "channel info & trading updates" in text:
        await update.message.reply_text(f"📌 **CHANNEL INFO**\n\nOfficial Channel: {CHANNEL}\n\nWe post:\n- Daily Signals\n- Trading Updates\n- Market News\n- Analysis")
    elif "contact our team" in text:
        await update.message.reply_text(f"📩 **CONTACT US**\n\nAdmin: {CONTACT}\nChannel: {CHANNEL}\n\nMessage us anytime!")
    elif "trading risk management tips" in text:
        await update.message.reply_text(
            "📊 **RISK MANAGEMENT TIPS**\n\n"
            "1️⃣ Risk only 1-2% per trade\n"
            "2️⃣ Always use Stop Loss\n"
            "3️⃣ Don't overtrade - 2-3 trades max per day\n"
            "4️⃣ Follow our SL/TP exactly\n"
            "5️⃣ Don't use high lot size"
        )
    elif "welcome! start here" in text:
        await start(update, context)
    elif "register with our trusted broker" in text:
        await update.message.reply_text(
            f"📝 **REGISTER WITH OUR TRUSTED BROKER**\n\n"
            f"Create account via our link to get VIP:\n\n{DERIV}\n\nAfter registration, click 'Verify Deriv Registration'",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📝 REGISTER NOW", url=DERIV)]])
        )
    elif "get vip access now" in text:
        await update.message.reply_text(
            f"🔥 **GET VIP ACCESS NOW** 🥺\n\n"
            f"To get VIP:\n"
            f"1. Register via: {DERIV}\n"
            f"2. Click 'Verify Deriv Registration'\n"
            f"3. Send your Deriv ID\n\n"
            f"You will get VIP signals FREE!"
        )
    elif "verify deriv registration" in text:
        await update.message.reply_text(
            "✅ **VERIFY DERIV REGISTRATION**\n\n"
            "Please send your Deriv ID / Email you used to register.\n\n"
            "Example: CR1234567 or your email\n\n"
            "We will verify within 5 minutes!"
        )
    elif "verification request submitted" in text:
        await update.message.reply_text(
            "✅ **Verification request submitted.**\n\n"
            "Thank you! We received your request.\n"
            "Our team will check and confirm your VIP status within 15 minutes.\n\n"
            "Please also send your 'Personal contact info for confirmation.'"
        )
    elif "personal contact info for confirmation" in text:
        await update.message.reply_text(
            "📞 **Personal contact info for confirmation.**\n\n"
            "Please send:\n"
            "1. Your Telegram @username\n"
            "2. Your WhatsApp number (optional)\n"
            "3. Your Deriv ID\n\n"
            "We will contact you once verified!"
        )
    elif "send new post to subscribers" in text:
        await update.message.reply_text(
            "📤 **Send New Post to Subscribers**\n\n"
            "This is Admin command.\n\n"
            "To broadcast, use format:\n"
            "/broadcast Your message here\n\n"
            "(Contact admin for broadcast access)"
        )
    elif "custom commands" in text:
        await update.message.reply_text(
            "⚙️ **Custom Commands**\n\n"
            "Available commands:\n"
            "/start - Restart bot\n"
            "All menu buttons work as commands\n\n"
            "Need help? Contact: @PipHuntersSignals2"
        )
    else:
        await start(update, context)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))
    app.run_polling()

if __name__ == "__main__":
    main()
