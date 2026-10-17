import os
import sqlite3
import threading
import logging
from datetime import datetime, timedelta
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
DERIV_LINK = "https://t.deriv.link?t=N886WMZM3C76"
FREE_CHANNEL_1 = "https://t.me/PipHuntersSignals1"
FREE_CHANNEL_2 = "@PipHuntersSignals2"
WHATSAPP = "+233596822581"
WHATSAPP_LINK = f"https://wa.me/233596822581"
ADMIN_ID = os.getenv("ADMIN_ID")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        username TEXT,
        last_action TEXT,
        last_time TEXT,
        finished INTEGER DEFAULT 0
    )""")
    conn.commit()
    conn.close()

def save_user(user, action="start", finished=0):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,?)",
              (user.id, user.first_name, user.username, action, datetime.utcnow().isoformat(), finished))
    conn.commit()
    conn.close()

def get_unfinished_users():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT user_id, first_name, last_action, last_time FROM users WHERE finished=0")
    rows = c.fetchall()
    conn.close()
    result = []
    for uid, fname, action, ltime in rows:
        try:
            lt = datetime.fromisoformat(ltime)
            if datetime.utcnow() - lt > timedelta(minutes=10):
                result.append((uid, fname, action))
        except: pass
    return result

def mark_finished(user_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET finished=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

init_db()

app = Flask(__name__)
@app.route("/")
def home():
    return "PIP HUNTERS BOT IS LIVE - 24/7"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
threading.Thread(target=run_flask, daemon=True).start()

def main_menu():
    keyboard = [
        ["📈 Get Free Trading Signals", "📢 Join Our Free Channel"],
        ["ℹ️ About Our Forex Academy", "🎓 Free Forex Education"],
        ["💼 Create Trading Account", "💬 Contact Support"],
        ["📊 Today's Market Overview", "🔔 Subscribe to VIP"],
        ["📉 Live Trading Session", "📚 Trading E-Book"],
        ["💹 Copy Trading Info", "🤖 Auto Trading Bot"],
        ["📅 Economic Calendar", "❓ FAQ"],
        ["📝 Send New Post to Subscribers"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user, action="start", finished=0)
    name = user.first_name
    text = f"🔥 Welcome back, *{name}*! \n\nI am *PIP HUNTERS SIGNALS* - Your No.1 Forex Partner in Ghana 🇬🇭\n\nWe help traders like you catch daily pips.\n\n👇 Choose what you want, {name}:"
    await update.message.reply_text(text, reply_markup=main_menu(), parse_mode="Markdown")
    save_user(user, action="clicked_start_but_no_action", finished=0)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    name = user.first_name
    if "Get Free Trading Signals" in text:
        save_user(user, action="get_free_signals_clicked", finished=0)
        msg = f"📈 Hey *{name}*, ready for free signals?\n\n1️⃣ Join Free Channel 👉 {FREE_CHANNEL_1}\n2️⃣ Backup: {FREE_CHANNEL_2}\n3️⃣ Create Deriv: {DERIV_LINK}\n\nClick 'I have Joined' after."
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Join Free Channel", url=FREE_CHANNEL_1)],
            [InlineKeyboardButton("💼 Create Deriv Account", url=DERIV_LINK)],
            [InlineKeyboardButton("✅ I have Joined", callback_data="joined")]
        ])
        await update.message.reply_text(msg, reply_markup=kb, parse_mode="Markdown")
    elif "Join Our Free Channel" in text:
        save_user(user, action="join_channel", finished=1)
        await update.message.reply_text(f"📢 {name}, join now 👉 {FREE_CHANNEL_1}\nBackup: {FREE_CHANNEL_2}", reply_markup=main_menu())
    elif "Create Trading Account" in text:
        save_user(user, action="create_account", finished=0)
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("💹 Create Deriv Now", url=DERIV_LINK)]])
        await update.message.reply_text(f"💼 {name}, create account here:\n👉 {DERIV_LINK}", reply_markup=kb)
    elif "Contact Support" in text:
        save_user(user, action="support", finished=1)
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("💬 WhatsApp Us", url=WHATSAPP_LINK)]])
        await update.message.reply_text(f"💬 {name}, WhatsApp: {WHATSAPP}\nWe reply in 5 mins!", reply_markup=kb)
    elif "Send New Post" in text:
        await update.message.reply_text(f"📝 {name}, to broadcast to ALL users:\n/broadcast YOUR MESSAGE\nExample: /broadcast BUY GOLD NOW SL 2640 TP 2660")
    else:
        save_user(user, action=text[:30], finished=1)
        await update.message.reply_text(f"Got it {name} 👍 Use menu:", reply_markup=main_menu())

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()
    if query.data == "joined":
        mark_finished(user.id)
        await query.edit_message_text(f"✅ Awesome {user.first_name}! Welcome! Signals dropping in {FREE_CHANNEL_1} soon.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ADMIN_ID and str(update.effective_user.id) != ADMIN_ID:
        await update.message.reply_text("⛔ Only admin can broadcast.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast Your message")
        return
    message = " ".join(context.args)
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = c.fetchall()
    conn.close()
    sent = 0
    for (uid,) in users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 *PIP HUNTERS UPDATE*\n\n{message}\n\nJoin: {FREE_CHANNEL_1}", parse_mode="Markdown")
            sent += 1
        except: pass
    await update.message.reply_text(f"✅ Sent to {sent} users!")

async def reminder_job(context: ContextTypes.DEFAULT_TYPE):
    for uid, fname, action in get_unfinished_users():
        try:
            if "get_free_signals" in action:
                await context.bot.send_message(chat_id=uid, text=f"⏰ Hey {fname}! You clicked Get Free Signals but didn't finish.\nYour spot: {FREE_CHANNEL_1}\nDeriv: {DERIV_LINK}")
            else:
                await context.bot.send_message(chat_id=uid, text=f"👋 {fname}, you left without finishing. Need help? {WHATSAPP_LINK}")
            mark_finished(uid)
        except Exception as e:
            logger.error(e)

def main():
    app_bot = Application.builder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("broadcast", broadcast))
    app_bot.add_handler(CallbackQueryHandler(button_callback))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_bot.job_queue.run_repeating(reminder_job, interval=600, first=30)
    app_bot.run_polling()

if __name__ == "__main__":
    main()
