import os, sqlite3, threading, logging
from datetime import datetime, timedelta
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
DERIV_LINK = "https://t.deriv.link?t=N886WMZM3C76"
FREE_CHANNEL_1 = "https://t.me/PipHuntersSignals1"
FREE_CHANNEL_2 = "@PipHuntersSignals2"
WHATSAPP = "+233596822581"
WHATSAPP_LINK = f"https://wa.me/{WHATSAPP}"
ADMIN_ID = os.getenv("ADMIN_ID")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, first_name TEXT, username TEXT, last_action TEXT, last_time TEXT, finished INTEGER DEFAULT 0)""")
    conn.commit()
    conn.close()

def save_user(user, action="start", finished=0):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,?)",(user.id, user.first_name, user.username, action, datetime.utcnow().isoformat(), finished))
    conn.commit()
    conn.close()

def get_unfinished():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT user_id, first_name, last_action, last_time FROM users WHERE finished=0")
    rows = c.fetchall()
    conn.close()
    res=[]
    for uid,fname,action,ltime in rows:
        try:
            lt=datetime.fromisoformat(ltime)
            if datetime.utcnow()-lt > timedelta(minutes=10):
                res.append((uid,fname,action))
        except: pass
    return res

def mark_finished(uid):
    conn=sqlite3.connect("users.db")
    c=conn.cursor()
    c.execute("UPDATE users SET finished=1 WHERE user_id=?",(uid,))
    conn.commit()
    conn.close()

init_db()
app = Flask(__name__)
@app.route("/")
def home(): return "PIP HUNTERS BOT LIVE 24/7"
def run_flask():
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)
threading.Thread(target=run_flask,daemon=True).start()

def main_menu():
    return ReplyKeyboardMarkup([
        ["Get Free Trading Signals", "Join Our Free Channel"],
        ["About Our Forex Academy", "Free Forex Education"],
        ["Create Trading Account", "Contact Support"],
        ["Today's Market Overview", "Subscribe to VIP"],
        ["Live Trading Session", "Trading E-Book"],
        ["Copy Trading Info", "Auto Trading Bot"],
        ["Economic Calendar", "FAQ"],
        ["Send New Post to Subscribers"]
    ], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user=update.effective_user
    save_user(user,"start",0)
    name=user.first_name
    text=f"🔥 Welcome {name}!\n\nI am *PIP HUNTERS SIGNALS* - Your No.1 Forex Partner in Ghana 🇬🇭\n\nWe give 3-5 accurate signals daily.\n\n👇 Choose what you want, {name}:"
    await update.message.reply_text(text, reply_markup=main_menu(), parse_mode="Markdown")
    save_user(user,"clicked_start_but_no_action",0)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user=update.effective_user
    t=update.message.text.lower()
    name=user.first_name
    
    if "free trading signals" in t:
        save_user(user,"get_free_signals_clicked",0)
        msg=f"📈 Hey {name}, ready for free signals?\n\n1️⃣ Join Free Channel 👉 {FREE_CHANNEL_1}\n2️⃣ Backup: {FREE_CHANNEL_2}\n3️⃣ Create Deriv: {DERIV_LINK}\n\nClick 'I have Joined' after."
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Join Free Channel", url=FREE_CHANNEL_1)],[InlineKeyboardButton("💼 Create Deriv Account", url=DERIV_LINK)],[InlineKeyboardButton("✅ I have Joined", callback_data="joined")]])
        await update.message.reply_text(msg, reply_markup=kb, parse_mode="Markdown")
        
    elif "join our free channel" in t or "join free channel" in t:
        save_user(user,"join_channel",1)
        await update.message.reply_text(f"📢 {name}, join here now 👉 {FREE_CHANNEL_1}\nBackup: {FREE_CHANNEL_2}\n\nYou will get 3-5 free signals daily!", reply_markup=main_menu())
        
    elif "about our forex" in t or "forex academy" in t:
        save_user(user,"about",1)
        await update.message.reply_text(f"ℹ️ *PIP HUNTERS ACADEMY*\n\nWe are Ghana's fastest growing forex community.\n\n📍 Accra, Ghana\n📞 Support: {WHATSAPP}\n\n{name}, join free channel: {FREE_CHANNEL_1}", parse_mode="Markdown", reply_markup=main_menu())
        
    elif "free forex education" in t or "education" in t:
        save_user(user,"education",1)
        await update.message.reply_text(f"🎓 {name}, your free lessons:\n\n1. What is Forex?\n2. Candlesticks\n3. Support & Resistance\n4. Risk Management\n\nFull course in channel: {FREE_CHANNEL_1}", reply_markup=main_menu())
        
    elif "create trading account" in t or "create deriv" in t:
        save_user(user,"create_account",0)
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("💹 Create Deriv Now", url=DERIV_LINK)]])
        await update.message.reply_text(f"💼 {name}, create account here:\n👉 {DERIV_LINK}\n\nUse this link to get VIP faster!", reply_markup=kb)
        
    elif "contact support" in t:
        save_user(user,"support",1)
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("💬 WhatsApp Us", url=WHATSAPP_LINK)]])
        await update.message.reply_text(f"💬 {name}, WhatsApp: {WHATSAPP}\nWe reply in 5 mins!", reply_markup=kb)
        
    elif "market overview" in t:
        save_user(user,"market_overview",1)
        await update.message.reply_text(f"📊 *Today Market Overview for {name}*\n\n• GOLD: Bullish above 2650\n• EURUSD: Waiting CPI news\n• VOL 75: Ranging\n• BTC: Volatile\n\nFull analysis: {FREE_CHANNEL_1}", parse_mode="Markdown", reply_markup=main_menu())
        
    elif "subscribe to vip" in t or "vip" in t:
        save_user(user,"vip_intent",0)
        await update.message.reply_text(f"🔔 {name}, VIP coming soon! Join free first and you will be first to get VIP:\n{FREE_CHANNEL_1}\n\nCreate Deriv via {DERIV_LINK} to qualify FREE!", reply_markup=main_menu())
        
    elif "live trading session" in t:
        save_user(user,"live_session",1)
        await update.message.reply_text(f"📉 {name}, Live Sessions: Tuesdays & Thursdays 8PM GMT in {FREE_CHANNEL_1}", reply_markup=main_menu())
        
    elif "trading e-book" in t or "e-book" in t or "ebook" in t:
        save_user(user,"ebook",1)
        await update.message.reply_text(f"📚 {name}, your FREE E-Book is being prepared. Stay in {FREE_CHANNEL_1} - we drop it this week!", reply_markup=main_menu())
        
    elif "copy trading" in t:
        save_user(user,"copy_trading",0)
        await update.message.reply_text(f"💹 {name}, Copy Trading coming soon. Create account now: {DERIV_LINK}", reply_markup=main_menu())
        
    elif "auto trading bot" in t:
        save_user(user,"auto_bot",1)
        await update.message.reply_text(f"🤖 {name}, Auto Bot under development. It will scan RSI/EMA and send alerts. Stay in {FREE_CHANNEL_1}", reply_markup=main_menu())
        
    elif "economic calendar" in t:
        save_user(user,"calendar",1)
        await update.message.reply_text(f"📅 {name}, Today High Impact:\n• 8:30 AM EST - USD CPI\n• Check forexfactory.com\nAvoid trading 10 mins before/after red news!", reply_markup=main_menu())
        
    elif "faq" in t:
        save_user(user,"faq",1)
        await update.message.reply_text(f"❓ FAQ for {name}:\n\nQ: Are signals free?\nA: Yes, 3-5 daily in {FREE_CHANNEL_2}\n\nQ: Guarantee profit?\nA: No. Forex risky. We provide analysis.\n\nQ: How to get VIP?\nA: Join channel + create Deriv via {DERIV_LINK}", reply_markup=main_menu())
        
    elif "send new post" in t:
        await update.message.reply_text(f"📝 {name}, to broadcast to ALL:\n/broadcast YOUR MESSAGE\nExample: /broadcast BUY GOLD NOW SL 2640 TP 2660")
    else:
        save_user(user,t[:30],1)
        await update.message.reply_text(f"{name}, use menu below 👇", reply_markup=main_menu())

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query=update.callback_query
    user=query.from_user
    await query.answer()
    if query.data=="joined":
        mark_finished(user.id)
        await query.edit_message_text(f"✅ Awesome {user.first_name}! Welcome aboard!\n\nSignals will drop in {FREE_CHANNEL_1} shortly!")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ADMIN_ID and str(update.effective_user.id)!=ADMIN_ID:
        await update.message.reply_text("⛔ Only admin.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast Your message")
        return
    message=" ".join(context.args)
    conn=sqlite3.connect("users.db")
    c=conn.cursor()
    c.execute("SELECT user_id FROM users")
    users=c.fetchall()
    conn.close()
    sent=0
    for (uid,) in users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 *PIP HUNTERS UPDATE*\n\n{message}\n\nJoin: {FREE_CHANNEL_1}", parse_mode="Markdown")
            sent+=1
        except: pass
    await update.message.reply_text(f"✅ Sent to {sent} users!")

async def reminder_job(context: ContextTypes.DEFAULT_TYPE):
    for uid,fname,action in get_unfinished():
        try:
            if "free_signals" in action:
                await context.bot.send_message(chat_id=uid, text=f"⏰ Hey {fname}! You clicked Get Free Signals but didn't finish.\nYour spot: {FREE_CHANNEL_1}\nDeriv: {DERIV_LINK}")
            else:
                await context.bot.send_message(chat_id=uid, text=f"👋 {fname}, you left without finishing. Need help? {WHATSAPP_LINK}")
            mark_finished(uid)
        except Exception as e: logger.error(e)

def main():
    if not TOKEN:
        logger.error("BOT_TOKEN not set!")
        return
    app_bot=Application.builder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("broadcast", broadcast))
    app_bot.add_handler(CallbackQueryHandler(button_callback))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    if app_bot.job_queue:
        app_bot.job_queue.run_repeating(reminder_job, interval=600, first=30)
    app_bot.run_polling()

if __name__=="__main__":
    main()
