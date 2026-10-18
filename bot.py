import os, json, logging, threading, datetime
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

flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Pip Hunters Bot V8.9 REAL CHARTS LIVE - 24/7"
@flask_app.route('/health')
def health(): return "OK", 200
def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def load_data():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    new_data = {}
                    for uid in data:
                        new_data[str(uid)] = {"id": uid, "last_action": "start", "last_seen": str(datetime.datetime.now()), "visits": 1}
                    return new_data
                return data
    except: pass
    return {}
def save_data(data):
    try:
        with open(USERS_FILE, "w") as f: json.dump(data, f, indent=2)
    except: pass
def update_user_memory(uid, username, firstname, action="start"):
    data = load_data(); uid_str = str(uid); now = str(datetime.datetime.now())
    if uid_str not in data:
        data[uid_str] = {"id": uid, "username": username, "name": firstname, "last_action": action, "last_seen": now, "visits": 1, "joined": now}
    else:
        data[uid_str]["last_action"] = action; data[uid_str]["last_seen"] = now; data[uid_str]["visits"] = data[uid_str].get("visits", 0) + 1
        data[uid_str]["username"] = username; data[uid_str]["name"] = firstname
    save_data(data); return data.get(uid_str)
def get_user_list():
    data = load_data(); return [v["id"] for v in data.values() if "id" in v]
def get_last_action(uid):
    return load_data().get(str(uid), {}).get("last_action", "start")

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📈 Free Trading Signals", callback_data='signals')],
        [InlineKeyboardButton("🚀 Join Free Channel", url=FREE_CHANNEL_LINK)],
        [InlineKeyboardButton("🎓 About Us", callback_data='about_academy')],
        [InlineKeyboardButton("📚 Free Education", callback_data='education')],
        [InlineKeyboardButton("🏦 Create Trading Account", url=DERIV_LINK)],
        [InlineKeyboardButton("🆘 Support", callback_data='support')],
        [InlineKeyboardButton("📊 Market Overview", callback_data='market')],
        [InlineKeyboardButton("💎 VIP Access", callback_data='vip')],
        [InlineKeyboardButton("📹 Live Trading", callback_data='live_session')],
        [InlineKeyboardButton("📖 Trading E-Book (5 REAL Charts)", callback_data='ebook')],
        [InlineKeyboardButton("👥 Copy Trading", callback_data='copytrading')],
        [InlineKeyboardButton("🤖 Auto Trading Bot", callback_data='autobot')],
        [InlineKeyboardButton("🗓️ Economic Calendar", callback_data='calendar')],
        [InlineKeyboardButton("❓ FAQ", callback_data='faq')],
        [InlineKeyboardButton("🛡️ Risk Management", callback_data='risk')],
    ])
def back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data='main')]])

async def send_real_charts(chat_id, context, include_ebook_text=False):
    charts = [
        ("chart_5_m30_14_oct_sweep.jpg", "📊 CHART 1: 14 Oct Sweep Model A\n\n4070 -> 4168.18 = +980 pips\nSweep liquidity then bullish reversal\nEntry at 4129 red box\nTarget 4168 magnet\n\n⚡ Pip Hunters REAL MT5"),
        ("chart_1_m30_15_16_oct_redboxes.jpg", "📊 CHART 2: 15-16 Oct Red Boxes\n\n4129 & 4168 Breaker Blocks\nM30 showing 4168.18 holding as key\nRed boxes = institutional order blocks\nPrice respects 4168 magnet\n\n⚡ Pip Hunters REAL MT5"),
        ("chart_3_m30_9_oct_rally.jpg", "📊 CHART 3: 9 Oct Rally\n\n4145 -> 4200+ rally\n5:00 GMT breakout\n4168.18 acted as support\nModel B entry\n\n⚡ Pip Hunters REAL MT5"),
        ("chart_4_m30_6_7_oct_doubletop.jpg", "📊 CHART 4: 6-7 Oct Double Top\n\n4176.65 double top -> 4055 sweep\n4168.18 breakdown\nWhy 4168 is critical decision point\n\n⚡ Pip Hunters REAL MT5"),
        ("chart_2_m15_16_oct_holding.jpg", "📊 CHART 5: M15 16 Oct Holding\n\n16 Oct 13:45 - 18:45\n4168.18 holding as support after drop\nM15 MSS entry model\nReal-time hold proof\n\n⚡ Pip Hunters REAL MT5"),
    ]
    if include_ebook_text:
        ebook_caption = f"📖 PIP HUNTERS E-BOOK + 5 REAL CHARTS\n\nPrice: $100 FREE today\n\nIncludes:\n• 4168.18 Magnet Explained\n• 10-Point Scoring (7/10 Rule)\n• London & NY Kill Zones\n• $100-$1000 Blueprint\n• Risk Formula\n• 5 REAL MT5 Charts\n\n👇 Below are your 5 REAL charts:\n\nJoin: {FREE_CHANNEL_LINK}\nBroker: {DERIV_LINK}"
        try: await context.bot.send_message(chat_id=chat_id, text=ebook_caption)
        except: pass
    for filename, caption in charts:
        try:
            if os.path.exists(filename):
                with open(filename, 'rb') as photo:
                    await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=caption)
            else:
                await context.bot.send_message(chat_id=chat_id, text=caption + "\n\n[Chart: "+filename+"]")
        except Exception as e:
            logging.error(f"Failed {filename}: {e}")
            try: await context.bot.send_message(chat_id=chat_id, text=caption)
            except: pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id; user = update.effective_user; data = load_data()
    is_returning = str(uid) in data; last_action = get_last_action(uid) if is_returning else "start"
    update_user_memory(uid, user.username, user.first_name, "start")
    try:
        if uid != ADMIN_ID:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔔 {'RETURNING' if is_returning else 'NEW'} USER\nName: {user.first_name} @{user.username}\nID: {uid}\nLast: {last_action}\nTotal: {len(load_data())}")
    except: pass
    name = user.first_name or "Trader"
    if is_returning and last_action != "start":
        resume_text = {"vip": "VIP Access", "signals": "Free Signals", "support": "Support", "about_academy": "About Us", "market": "Market Overview", "education": "Free Education", "live_session": "Live Trading", "ebook": "E-Book", "copytrading": "Copy Trading"}.get(last_action, last_action)
        text = f"Welcome back {name}! 👋\n\nYou left off at: *{resume_text}*\n\nWe saved your place. Continue where you left off?\n\nSelect below:"
    else:
        text = f"Welcome {name} to Pip Hunters\n\nProfessional Forex & Gold Signals Provider\nAccuracy: 85-90% | 3-5 Signals Daily\n\nSelect an option below:"
    await update.message.reply_text(text, reply_markup=main_menu())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🆘 Help: /start for menu\nAll features include 5 REAL MT5 charts at 4168.18\nSupport: @PipHuntersSignals2", reply_markup=main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer(); data = query.data; uid = query.from_user.id
    update_user_memory(uid, query.from_user.username, query.from_user.first_name, data)
    try:
        if uid != ADMIN_ID:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"💬 CLICK: {data}\nFrom: {query.from_user.first_name} @{query.from_user.username} ({uid})")
    except: pass
    if data in ['main', 'welcome']:
        await query.message.reply_text("📋 Main Menu - Select an option:", reply_markup=main_menu())
    elif data == 'signals':
        await query.message.reply_text("📈 Free Trading Signals\n\nAll signals are posted live in our official channel:\n"+FREE_CHANNEL_LINK+"\n\n• 3-5 signals daily\n• XAUUSD, EURUSD, GBPUSD\n• With entry, SL, TP\n• Only at 4168.18 ±5 pips with 7/10 scoring\n\nEnable notifications.", reply_markup=back_menu())
    elif data == 'about_academy':
        await query.message.reply_text("🎓 About Pip Hunters\n\nProfessional trading community est. 2021\n\nWe specialize in:\n• Smart Money Concept (SMC)\n• Price Action & Liquidity\n• XAUUSD & Indices\n• Risk Management\n\nOur Mission: Help traders become profitable\n\nOfficial Channels:\n"+FREE_CHANNEL_LINK+"\n\n© 2026 Pip Hunters", reply_markup=back_menu())
    elif data == 'education':
        await query.message.reply_text("📚 Free Education\n\nBeginner Modules:\n1. Market Structure\n2. Support & Resistance\n3. Risk Management Basics\n4. SMC Introduction\n\nFull advanced course available for VIP members.\n\nCheck channel for daily lessons with REAL 4168 charts.", reply_markup=back_menu())
    elif data == 'support':
        kb = [[InlineKeyboardButton("💬 Contact Support", url=f"https://t.me/{BACKUP_CHANNEL.replace('@','')}")],[InlineKeyboardButton("⬅️ Back", callback_data='main')]]
        await query.message.reply_text("🆘 Support Center\n\nOur support team is available 24/5 (Mon-Fri)\n\nResponse time: 5-15 mins\n\nClick below to contact:", reply_markup=InlineKeyboardMarkup(kb))
    elif data == 'market':
        await query.message.reply_text("📊 Market Overview\n\nDaily analysis schedule (GMT):\n• 09:00 - London Open\n• 12:00 - Midday Update\n• 16:00 - NY Session\n\nAll analysis posted in:\n"+FREE_CHANNEL_LINK+"\n\nWe trade REAL 4168.18 level only.", reply_markup=back_menu())
    elif data == 'vip':
        kb = [[InlineKeyboardButton("1️⃣ Register Account", url=DERIV_LINK)],[InlineKeyboardButton("2️⃣ Verify Registration", callback_data='verify')],[InlineKeyboardButton("⬅️ Back", callback_data='main')]]
        await query.message.reply_text("💎 VIP Access - FREE Membership\n\nBenefits:\n• 5-7 Premium Signals Daily\n• Higher Accuracy\n• Live Trading Sessions\n• Private Education\n• 5 REAL MT5 Charts Analysis\n\nHow to join FREE:\n1. Create account via button below\n2. Send screenshot of dashboard HERE (to this bot)\n3. Get activated in 10 mins", reply_markup=InlineKeyboardMarkup(kb))
    elif data == 'live_session':
        await query.message.reply_text("📹 Live Trading Sessions\n\nSchedule:\n• Tuesdays: 20:00 GMT\n• Thursdays: 20:00 GMT\n\nHosted live in our main channel:\n"+FREE_CHANNEL_LINK+"\n\nLive market breakdown + Q&A with REAL charts", reply_markup=back_menu())
    elif data == 'ebook':
        await query.message.reply_text("📖 Preparing your E-Book with 5 REAL MT5 Charts...\n\nPlease wait, sending charts now... ⏳", reply_markup=back_menu())
        await send_real_charts(query.message.chat_id, context, include_ebook_text=True)
        await query.message.reply_text(f"✅ E-Book + 5 REAL Charts Sent!\n\nAll charts are REAL from MT5, not drawings\nValue $100 - FREE today\n\nTo get full 50-page PDF:\nVerify here: {DERIV_LINK}\n\nJoin: {FREE_CHANNEL_LINK}", reply_markup=back_menu())
    elif data == 'copytrading':
        await query.message.reply_text("👥 Copy Trading Service\n\n• Minimum: $100\n• Automated copying\n• Full transparency\n• Monthly profit share\n• Based on 4168.18 strategy\n\nContact support to join.", reply_markup=back_menu())
    elif data == 'autobot':
        await query.message.reply_text("🤖 Auto Trading Bot\n\n• Gold (XAUUSD) Specialist\n• 24/5 Automated\n• Tested Strategy at 4168\n• VPS Required\n\nContact support for details.", reply_markup=back_menu())
    elif data == 'calendar':
        await query.message.reply_text("🗓️ Economic Calendar\n\nAlways check high-impact news before trading:\n• ForexFactory.com\n• Avoid trading 15 mins before/after RED news\n\nWe post news reminders in channel.", reply_markup=back_menu())
    elif data == 'faq':
        await query.message.reply_text("❓ FAQ\n\nQ: Are signals free?\nA: Yes, free signals in public channel\n\nQ: Accuracy?\nA: 85-90% with proper risk management at 4168\n\nQ: Which broker?\nA: We recommend Deriv via our official link\n\nQ: VIP cost?\nA: FREE when you register via our link\n\nQ: Are charts real?\nA: YES, all 5 charts are REAL MT5 screenshots", reply_markup=back_menu())
    elif data == 'risk':
        await query.message.reply_text("🛡️ Risk Management\n\nGolden Rules:\n• Risk 1-2% per trade max\n• Always use Stop Loss\n• Don't overtrade\n• Follow 1:2 RR minimum\n• Only trade 4168 ±5 pips with 7/10 score\n\nThis is not financial advice. Trade at your own risk.", reply_markup=back_menu())
    elif data == 'verify':
        await query.message.reply_text(f"✅ Verification Steps\n\n1. Register here: {DERIV_LINK}\n2. Take screenshot of your Deriv dashboard (show your name/ID)\n3. SEND THAT SCREENSHOT HERE as photo to this bot\n\nOur team verifies manually in 10 mins.", reply_markup=back_menu())
    elif data.startswith("approve_"):
        target_id = int(data.split("_")[1])
        try:
            await context.bot.send_message(chat_id=target_id, text="✅ Congratulations! You are VERIFIED!\n\n🎉 VIP Access Activated!\n\nYour E-Book and VIP channel access will be sent shortly.\n\nWelcome to Pip Hunters VIP!")
            await query.message.reply_text(f"✅ Approved user {target_id} - VIP activated!")
        except Exception as e: await query.message.reply_text(f"Failed: {e}")
    elif data.startswith("reject_"):
        target_id = int(data.split("_")[1])
        try:
            await context.bot.send_message(chat_id=target_id, text=f"❌ Verification Failed\n\nWe could not verify your account.\n\nPlease ensure:\n1. You registered via our link: {DERIV_LINK}\n2. Screenshot clearly shows your Deriv dashboard\n\nPlease try again.")
            await query.message.reply_text(f"❌ Rejected {target_id}")
        except Exception as e: await query.message.reply_text(f"Failed: {e}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id; user = update.effective_user
    update_user_memory(uid, user.username, user.first_name, "photo_verification")
    try:
        caption = f"📸 NEW VERIFICATION\nFrom: {user.first_name} @{user.username}\nID: {uid}\nLast: {get_last_action(uid)}"
        keyboard = [[InlineKeyboardButton("✅ Approve VIP", callback_data=f"approve_{uid}"), InlineKeyboardButton("❌ Reject", callback_data=f"reject_{uid}")]]
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard))
        await update.message.forward(chat_id=ADMIN_ID)
    except: pass
    await update.message.reply_text("📥 Screenshot Received!\n\nOur team is checking your registration...\nYou will be confirmed within 10 minutes. Please wait! ⏳", reply_markup=back_menu())

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id; text = update.message.text
    if text.startswith("/"): return
    update_user_memory(uid, update.effective_user.username, update.effective_user.first_name, f"text: {text[:20]}")
    try:
        if uid != ADMIN_ID:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"💬 MESSAGE\nFrom: {update.effective_user.first_name} @{update.effective_user.username} ({uid})\nMsg: {text}\n\nReply: /reply {uid} your msg")
    except: pass
    await update.message.reply_text("Thanks for your message! Our team will reply soon.\n\nSelect from menu for faster help:", reply_markup=main_menu())

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Only admin."); return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast Your message OR /reply USER_ID message"); return
    if context.args[0].isdigit() and update.message.text.startswith("/reply"):
        target_id = int(context.args[0]); msg = " ".join(context.args[1:])
        try:
            await context.bot.send_message(chat_id=target_id, text=f"📩 Message from Pip Hunters Support:\n\n{msg}")
            await update.message.reply_text(f"✅ Replied to {target_id}")
        except Exception as e: await update.message.reply_text(f"Failed: {e}")
        return
    msg = " ".join(context.args); users = get_user_list(); count = 0
    for uid in users:
        try: await context.bot.send_message(chat_id=uid, text=msg, parse_mode="HTML"); count += 1
        except: pass
    try: await context.bot.send_message(chat_id=CHANNEL_1, text=msg, parse_mode="HTML"); ch = f"Posted to {CHANNEL_1}"
    except Exception as e: ch = f"Make bot ADMIN in {CHANNEL_1}: {e}"
    await update.message.reply_text(f"Sent to {count} users\n{ch}")

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("reply", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Bot V8.9 REAL CHARTS EDITION - 24/7 Keep-Alive LIVE!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
