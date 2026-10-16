 import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# --- KEEP ALIVE SERVER FOR RENDER (Keeps bot Live for FREE) ---
class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"PIP HUNTERS Bot is Live!")
    def log_message(self, format, *args):
        return

def run_keep_alive_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), MyHandler)
    server.serve_forever()

threading.Thread(target=run_keep_alive_server, daemon=True).start()
# --- END KEEP ALIVE SERVER ---

TOKEN = os.getenv("BOT_TOKEN")
DERIV_LINK = "https://t.deriv.link?t=N886WMZM3C76"
CHANNEL = "https://t.me/PipHuntersSignals1"
USERNAME = "@PipHuntersSignals2"

WELCOME_TEXT = """🔥 Welcome to PIP HUNTERS SIGNALS 🔥

We provide FREE Forex Signals Daily!

Click below to get started 👇
"""

async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("✅ JOIN FREE SIGNALS CHANNEL", url=CHANNEL)],
        [InlineKeyboardButton("🔗 Create Deriv Account", url=DERIV_LINK)],
        [InlineKeyboardButton("📞 Contact Admin", url=f"https://t.me/{USERNAME.replace('@','')}")],
        [InlineKeyboardButton("▶️ How it Works", callback_data="how")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_TEXT, reply_markup=reply_markup)

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "how":
        text = """📈 How PIP HUNTERS Works:

1️⃣ Join our FREE channel
2️⃣ Create Deriv account via our link
3️⃣ Get daily signals + guidance

We help you grow! 💰"""
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "back":
        keyboard = [
            [InlineKeyboardButton("✅ JOIN FREE SIGNALS CHANNEL", url=CHANNEL)],
            [InlineKeyboardButton("🔗 Create Deriv Account", url=DERIV_LINK)],
            [InlineKeyboardButton("📞 Contact Admin", url=f"https://t.me/{USERNAME.replace('@','')}")],
            [InlineKeyboardButton("▶️ How it Works", callback_data="how")]
        ]
        await query.edit_message_text(WELCOME_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("PIP HUNTERS Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
