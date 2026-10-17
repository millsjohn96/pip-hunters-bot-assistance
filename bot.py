import os, json, logging, threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_1 = "@PipHuntersSignals1"
FREE_CHANNEL_LINK = "https://t.me/PipHuntersSignals1"
DERIV_LINK = "https://t.deriv.link?t=N886WMZM3C76"
BACKUP_CHANNEL = "@PipHuntersSignals2"
USERS_FILE = "users.json"

logging.basicConfig(level=logging.INFO)

# === FAKE WEBSITE FOR RENDER (THIS FIXES THE LOG ERROR) ===
flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "Pip Hunters Bot is LIVE!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

# === USERS DB ===
def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                return json.load(f)
    except: pass
    return []

def save_users(users):
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)
    except: pass

def add_user(uid):
    users = load_users()
    if uid not in users:
        users.append(uid)
        save_users(users)

def main_menu():
    keyboard = [
        [InlineKeyboardButton("📈 Free Trading Signals", callback_data='signals')],
        [InlineKeyboardButton("🚀 Join Free Channel", url=FREE_CHANNEL_LINK)],
        [InlineKeyboardButton("🎓 About Us", callback_data='about_academy')],
        [InlineKeyboardButton("📚 Free Education", callback_data='education')],
        [InlineKeyboardButton("🏦 Create Trading Account", url=DERIV_LINK)],
        [InlineKeyboardButton("🆘 Support", callback_data='support')],
        [InlineKeyboardButton("📊 Market Overview", callback_data='market')],
        [InlineKeyboardButton("💎 VIP Access", callback_data='vip')],
        [InlineKeyboardButton("📹 Live Trading", callback_data='live_session')],
        [InlineKeyboardButton("📖 Trading E-Book", callback_data='ebook')],
        [InlineKeyboardButton("👥 Copy Trading", callback_data='copytrading')],
        [InlineKeyboardButton("🤖 Auto Trading Bot", callback_data='autobot')],
        [InlineKeyboardButton("🗓️ Economic Calendar", callback_data='calendar')],
        [InlineKeyboardButton("❓ FAQ", callback_data='faq')],
        [InlineKeyboardButton("🛡️ Risk Management", callback_data='risk')],
    ]
    return InlineKeyboardMarkup(keyboard)

def back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data='main')]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    add_user(uid)
    name = update.effective_user.first_name or "Trader"
    try:
        if uid != ADMIN_ID:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔔 NEW USER: {name} @{update.effective_user.username} ID:{uid} Total:{len(load_users())}")
    except: pass
    text = f"Welcome {name} to Pip Hunters\n\nProfessional Forex & Gold Signals Provider\nAccuracy: 85-90% | 3-5 Signals Daily\n\nSelect an option below:"
    await update.message.reply_text(text, reply_markup=main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    try:
        if query.from_user.id != ADMIN_ID:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"💬 USER CLICKED: {data}\nFrom: {query.from_user.first_name} @{query.from_user.username} ({query.from_user.id})")
    except: pass

    if data in ['main', 'welcome']:
        await query.message.reply_text("Main Menu:", reply_markup=main_menu())
    elif data == 'signals':
        await query.message.reply_text(f"Free Signals\n\nAll signals in:\n{FREE_CHANNEL_LINK}", reply_markup=back_menu())
    elif data == 'about_academy':
        await query.message.reply_text("About Pip Hunters\n\nProfessional trading community providing Forex, Gold and Indices analysis.\n• SMC & Price Action\n• XAUUSD, NAS100\n© 2026 Pip Hunters", reply_markup=back_menu())
    elif data == 'education':
        await query.message.reply_text("Free Education\n1. Market Structure\n2. Support & Resistance\n3. Risk Management\n4. SMC Basics", reply_markup=back_menu())
    elif data == 'support':
        kb = [[InlineKeyboardButton("💬 Contact on Telegram", url=f"https://t.me/{BACKUP_CHANNEL.replace('@','')}")],[InlineKeyboardButton("⬅️ Back", callback_data='main')]]
        await query.message.reply_text("Support Center\nTeam available 24/5.", reply_markup=InlineKeyboardMarkup(kb))
    elif data == 'market':
        await query.message.reply_text(f"Market Overview\nAnalysis 3x daily: 09:00, 12:00, 16:00 GMT\nCheck {FREE_CHANNEL_LINK}", reply_markup=back_menu())
    elif data == 'vip':
        kb = [[InlineKeyboardButton("Register Account", url=DERIV_LINK)],[InlineKeyboardButton("Verify Registration", callback_data='verify')],[InlineKeyboardButton("⬅️ Back", callback_data='main')]]
        await query.message.reply_text("VIP Membership\nBenefits: 5-7 Signals, Live Trading\n1. Create account via link\n2. Send screenshot HERE\n3. Get activated", reply_markup=InlineKeyboardMarkup(kb))
    elif data == 'live_session':
        await query.message.reply_text(f"Live Trading\nTuesdays & Thursdays 20:00 GMT\nLive in {FREE_CHANNEL_LINK}", reply_markup=back_menu())
    elif data == 'ebook':
        await query.message.reply_text("E-Book\n50-page SMC E-Book for registered members.", reply_markup=back_menu())
    elif data == 'copytrading':
        await query.message.reply_text("Copy Trading\nMin $100. Contact support.", reply_markup=back_menu())
    elif data == 'autobot':
        await query.message.reply_text("Auto Bot\n24/5 Gold system. Contact support.", reply_markup=back_menu())
    elif data == 'calendar':
        await query.message.reply_text("Economic Calendar\nAvoid trading before/after red news. forexfactory.com", reply_markup=back_menu())
    elif data == 'faq':
        await query.message.reply_text("FAQ\nFree? Yes in channel\nAccuracy? 85-90%", reply_markup=back_menu())
    elif data == 'risk':
        await query.message.reply_text("Risk Management\nRisk 1-2% per trade. Always use SL.", reply_markup=back_menu())
    elif data == 'verify':
        await query.message.reply_text(f"Verification\n1. Register: {DERIV_LINK}\n2. Screenshot dashboard\n3. SEND PHOTO HERE now!", reply_markup=back_menu())
    elif data.startswith("approve_"):
        target_id = int(data.split("_")[1])
        try:
            await context.bot.send_message(chat_id=target_id, text="✅ VERIFIED! VIP Activated!\nJoin VIP: @PipHuntersSignals1")
            await query.message.reply_text(f"✅ Approved {target_id}")
        except Exception as e:
            await query.message.reply_text(f"Failed: {e}")
    elif data.startswith("reject_"):
        target_id = int(data.split("_")[1])
        try:
            await context.bot.send_message(chat_id=target_id, text=f"❌ Verification Failed\nRegister via {DERIV_LINK} and send correct screenshot.")
            await query.message.reply_text(f"❌ Rejected {target_id}")
        except Exception as e:
            await query.message.reply_text(f"Failed: {e}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = update.effective_user
    add_user(uid)
    try:
        caption = f"📸 NEW VERIFICATION\nFrom: {user.first_name} @{user.username}\nID: {uid}"
        keyboard = [[InlineKeyboardButton("✅ Approve VIP", callback_data=f"approve_{uid}"), InlineKeyboardButton("❌ Reject", callback_data=f"reject_{uid}")]]
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard))
        await update.message.forward(chat_id=ADMIN_ID)
    except: pass
    await update.message.reply_text("📥 Screenshot Received! Checking...\nYou will be confirmed in 10 mins. ⏳", reply_markup=back_menu())

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text
    if text.startswith("/"): return
    add_user(uid)
    try:
        if uid != ADMIN_ID:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"💬 MESSAGE\nFrom: {update.effective_user.first_name} @{update.effective_user.username} ({uid})\nMsg: {text}\n\nReply: /reply {uid} your msg")
    except: pass
    await update.message.reply_text("Thanks! Team will reply soon.", reply_markup=main_menu())

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Only admin.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast Your message OR /reply USER_ID message")
        return
    if context.args[0].isdigit() and update.message.text.startswith("/reply"):
        target_id = int(context.args[0])
        msg = " ".join(context.args[1:])
        try:
            await context.bot.send_message(chat_id=target_id, text=f"📩 Support:\n\n{msg}")
            await update.message.reply_text(f"✅ Replied to {target_id}")
        except Exception as e:
            await update.message.reply_text(f"Failed: {e}")
        return
    msg = " ".join(context.args)
    users = load_users()
    count = 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=msg, parse_mode="HTML")
            count += 1
        except: pass
    try:
        await context.bot.send_message(chat_id=CHANNEL_1, text=msg, parse_mode="HTML")
        ch = f"Posted to {CHANNEL_1}"
    except Exception as e:
        ch = f"Make bot ADMIN in {CHANNEL_1}: {e}"
    await update.message.reply_text(f"Sent to {count} users\n{ch}")

def main():
    # Start fake website in background - THIS FIXES RENDER LOG
    threading.Thread(target=run_flask, daemon=True).start()
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("reply", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Bot LIVE with Flask port fix!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
