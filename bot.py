import os, json, logging, threading, datetime, glob, time, requests
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
def home():
    return "Pip Hunters V10.6 FIXED LIVE 24/7"

@flask_app.route('/health')
def health():
    return "OK", 200

def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def keep_alive_ping():
    while True:
        time.sleep(600)
        try:
            url = os.getenv("RENDER_EXTERNAL_URL")
            if url:
                requests.get(url, timeout=10)
        except Exception as e:
            print(f"Ping error {e}")

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
    except Exception as e:
        print(f"Load error {e}")
    return {}

def save_data(data):
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Save error {e}")

def update_user_memory(uid, username, firstname, action="start"):
    data = load_data()
    uid_str = str(uid)
    now = str(datetime.datetime.now())
    if uid_str not in data:
        data[uid_str] = {"id": uid, "username": username, "name": firstname, "last_action": action, "last_seen": now, "visits": 1, "joined": now}
    else:
        data[uid_str]["last_action"] = action
        data[uid_str]["last_seen"] = now
        data[uid_str]["visits"] = data[uid_str].get("visits", 0) + 1
        data[uid_str]["username"] = username
        data[uid_str]["name"] = firstname
    save_data(data)
    return data.get(uid_str)

def get_user_list():
    data = load_data()
    return [v["id"] for v in data.values() if "id" in v]

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
    captions = [
        "📊 CHART 1: 14th Oct - Sweep Model A (BUY)\n\nClassic liquidity sweep. Price swept below 4070 taking early buyers SL. After sweep strong bullish MSS. Red box 4129 was institutional order block entry. Rallied to 4168 liquidity magnet. This is how Smart Money traps retail before real move. Never buy before sweep.",
        "📊 CHART 2: 15th-16th Oct - Institutional Red Boxes\n\nM30 showing two breaker blocks. Market marked 4129 and 4168 as critical decision points where banks placed orders. Price respects 4168 as support/resistance multiple times. Red boxes are where Smart Money waits. Understand boxes = stop chasing, start waiting at right zones.",
        "📊 CHART 3: 9th Oct - Early Morning Rally Model B\n\nBeautiful 5AM GMT breakout. Consolidating 4145 Asian. London killzone broke structure bullish with displacement. 4168 resistance flipped to support. This is Model B Breaker retest. Many missed because sleeping but system caught exact entry. London open powerful.",
        "📊 CHART 4: 6th-7th Oct - Double Top Reversal SELL\n\nDouble top failure. Two attempts to break 4176 failed equal highs = trap for breakout buyers. After second rejection collapsed to 4055 sweeping weak longs. Breakdown below 4168 confirmed shift. Teaches why we never buy double tops without confirmation - wait for sweep first.",
        "📊 CHART 5: 16th Oct M15 - Intraday Holding & MSS\n\nM15 execution 13:45-18:45 16th Oct. After sell-off price returned to 4168 and held above. Holding + MSS M15 gave high-prob long entry. Price respects level for hours. Real proof institutional levels hold even volatile days. Exactly how we time entries."
    ]
    proper = ["chart_5_m30_14_oct_sweep.jpg","chart_1_m30_15_16_oct_redboxes.jpg","chart_3_m30_9_oct_rally.jpg","chart_4_m30_6_7_oct_doubletop.jpg","chart_2_m15_16_oct_holding.jpg"]
    found = [f for f in proper if os.path.exists(f)]
    if len(found) < 5:
        all_imgs = glob.glob("*.jpg") + glob.glob("*.JPG") + glob.glob("*.jpeg") + glob.glob("*.png") + glob.glob("IMG-*") + glob.glob("*.PNG")
        all_imgs = sorted(list(set(all_imgs)))
        if len(all_imgs) >= 5:
            found = all_imgs[:5]
        elif all_imgs:
            found = all_imgs
    if include_ebook_text:
        txt = f"📖 PIP HUNTERS E-BOOK + 5 REAL CHARTS\n\nPrice: $100 - FREE Today Only!\nInside Learn: Order Blocks, 7/10 Scoring, Kill Zones, $100-$1000 Blueprint, Risk Management, 5 REAL MT5 Breakdowns\n\nBelow are 5 REAL MT5 charts:\nJoin: {FREE_CHANNEL_LINK}\nAccount: {DERIV_LINK}"
        try:
            await context.bot.send_message(chat_id=chat_id, text=txt)
        except Exception as e:
            print(e)
    if not found:
        await context.bot.send_message(chat_id=chat_id, text="Charts uploading... try again 1 minute")
        return
    for idx, fn in enumerate(found):
        try:
            cap = captions[idx] if idx < len(captions) else f"REAL CHART {idx+1}"
            if os.path.exists(fn):
                with open(fn, 'rb') as ph:
                    await context.bot.send_photo(chat_id=chat_id, photo=ph, caption=cap)
        except Exception as e:
            logging.error(f"Failed {fn}: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = update.effective_user
    data = load_data()
    is_returning = str(uid) in data
    last_action = get_last_action(uid) if is_returning else "start"
    update_user_memory(uid, user.username, user.first_name, "start")
    try:
        if uid != ADMIN_ID:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"NEW USER: {user.first_name} @{user.username} ID:{uid} Last:{last_action} Total:{len(load_data())}")
    except Exception as e:
        print(e)
    name = user.first_name or "Trader"
    text = f"Welcome {name} to Pip Hunters\n\nProfessional Forex & Synthetic Indices Signals Provider\nAccuracy: 85-90% | 3-5 Signals Daily\n\nSelect option:"
    await update.message.reply_text(text, reply_markup=main_menu())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Help: /start for menu", reply_markup=main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = query.from_user.id
    update_user_memory(uid, query.from_user.username, query.from_user.first_name, data)
    try:
        if uid != ADMIN_ID:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"CLICK: {data} From: {query.from_user.first_name} @{query.from_user.username} ({uid})")
    except Exception as e:
        print(e)

    if data in ['main', 'welcome']:
        await query.message.reply_text("Main Menu:", reply_markup=main_menu())
    elif data == 'signals':
        await query.message.reply_text(f"Free Trading Signals\n\nAll signals in official channel:\n{FREE_CHANNEL_LINK}\n\n- 3-5 high-quality signals daily\n- XAUUSD, Forex & Synthetic Indices\n- Clear Entry, SL and TP", reply_markup=back_menu())
    elif data == 'about_academy':
        await query.message.reply_text(f"About Pip Hunters\n\nProfessional trading community established in 2020\n\nSpecialized in:\n- SMC\n- Price Action & Liquidity\n- Technical Analysis & Market Structure\n- Forex & Synthetic Indices\n- Risk Management & Psychology\n- Boom & Crash & Volatility Mastery\n\nWe trade both Forex and Synthetic with institutional approach.\n\nChannel:\n{FREE_CHANNEL_LINK}\n\n2026 Pip Hunters", reply_markup=back_menu())
    elif data == 'education':
        await query.message.reply_text("Free Education Hub\n\n1 Market Structure\n2 Support & Resistance\n3 Risk Management\n4 Intro to SMC\n5 Synthetic Basics", reply_markup=back_menu())
    elif data == 'support':
        kb = [[InlineKeyboardButton("Contact Support", url=f"https://t.me/{BACKUP_CHANNEL.replace('@','')}")],[InlineKeyboardButton("Back", callback_data='main')]]
        await query.message.reply_text("Support Center 24/5 Mon-Fri Response 5-15 mins", reply_markup=InlineKeyboardMarkup(kb))
    elif data == 'market':
        await query.message.reply_text(f"Market Overview\n\nSchedule GMT:\n- 09:00 London Open\n- 12:00 Midday\n- 16:00 NY\n\nAll in:\n{FREE_CHANNEL_LINK}", reply_markup=back_menu())
    elif data == 'vip':
        kb = [[InlineKeyboardButton("1 Register Account", url=DERIV_LINK)],[InlineKeyboardButton("2 Verify Registration", callback_data='verify')],[InlineKeyboardButton("Back", callback_data='main')]]
        await query.message.reply_text("VIP Access FREE\n\n- 5-7 Premium Signals Daily\n- Higher Accuracy & Better R:R\n- Live Trading (Coming Soon)\n- Private Education\n- Priority Support\n\nHow to join FREE:\n1 Create account\n2 Send screenshot HERE\n3 Activated 10 mins", reply_markup=InlineKeyboardMarkup(kb))
    elif data == 'live_session':
        await query.message.reply_text(f"Live Trading Sessions\n\nPreparing to launch live sessions breakdown real-time.\n\nTuesdays 20:00 GMT\nThursdays 20:00 GMT\n\nAnnouncements in:\n{FREE_CHANNEL_LINK}", reply_markup=back_menu())
    elif data == 'ebook':
        await query.message.reply_text("Preparing E-Book with 5 REAL MT5 Charts... wait...", reply_markup=back_menu())
        await send_real_charts(query.message.chat_id, context, include_ebook_text=True)
        await query.message.reply_text(f"E-Book + 5 REAL Charts Sent! FREE today Join: {FREE_CHANNEL_LINK}", reply_markup=back_menu())
    elif data == 'copytrading':
        await query.message.reply_text("Copy Trading Service\n\nWorking on launching professional copy trading.\n\nPlanned: Min $100, Fully Automated, Transparency, Risk Management, Forex & Synthetic.\n\nNot live yet finalizing system for safety. Stay tuned for launch.", reply_markup=back_menu())
    elif data == 'autobot':
        await query.message.reply_text("Auto Trading Bot\n\nDeveloping Gold XAUUSD and Synthetic Bot.\n\nFeatures: 24/5 Automated, Tested Institutional Strategy, VPS, Risk Management\n\nNot available public yet testing phase. Contact support early access.", reply_markup=back_menu())
    elif data == 'calendar':
        await query.message.reply_text("Economic Calendar\nCheck ForexFactory.com Avoid 15 mins before after RED news", reply_markup=back_menu())
    elif data == 'faq':
        await query.message.reply_text("FAQ 8 Questions\n\n1 Free? Yes 3-5 daily public channel VIP extra.\n\n2 Accuracy? 85-90% when risk rules followed.\n\n3 Markets? Forex Majors + XAUUSD + Synthetic Volatility Boom Crash.\n\n4 Broker? Deriv fast execution low spreads official link.\n\n5 How much start? $50-$100, recommend $100+ risk 1-2% per trade.\n\n6 VIP free? Yes free create account partner link send screenshot verification.\n\n7 Mentorship? Yes free education channel private mentorship SMC Price Action Psychology.\n\n8 Contact support? Support button menu Telegram 5-15 mins weekdays.", reply_markup=back_menu())
    elif data == 'risk':
        await query.message.reply_text("Risk Management\n\nGolden Rules:\n- Risk only 1-2% per trade most important\n- Always Stop Loss\n- Don't overtrade\n- Minimum 1:2 R:R\n- Trade with caution discipline\n- Breaks after 2 losses\n\nProtecting capital > making profit. Not financial advice.", reply_markup=back_menu())
    elif data == 'verify':
        await query.message.reply_text(f"Verification Steps\n\n1 Register: {DERIV_LINK}\n2 Screenshot Deriv dashboard\n3 SEND HERE as photo\n\nVerify 10 mins.", reply_markup=back_menu())
    elif data.startswith("approve_"):
        target_id = int(data.split("_")[1])
        try:
            await context.bot.send_message(chat_id=target_id, text="Congratulations! VERIFIED! VIP Activated! Welcome to Pip Hunters VIP!")
            await query.message.reply_text(f"Approved {target_id}")
        except Exception as e:
            await query.message.reply_text(f"Failed {e}")
    elif data.startswith("reject_"):
        target_id = int(data.split("_")[1])
        try:
            await context.bot.send_message(chat_id=target_id, text=f"Verification Failed. Ensure registered via link {DERIV_LINK} and screenshot shows dashboard clearly.")
            await query.message.reply_text(f"Rejected {target_id}")
        except Exception as e:
            await query.message.reply_text(f"Failed {e}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = update.effective_user
    update_user_memory(uid, user.username, user.first_name, "photo_verification")
    try:
        caption = f"NEW VERIFICATION From: {user.first_name} @{user.username} ID:{uid} Last:{get_last_action(uid)}"
        keyboard = [[InlineKeyboardButton("Approve VIP", callback_data=f"approve_{uid}"), InlineKeyboardButton("Reject", callback_data=f"reject_{uid}")]]
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard))
        await update.message.forward(chat_id=ADMIN_ID)
    except Exception as e:
        print(e)
    await update.message.reply_text("Screenshot Received! Checking... confirmed within 10 mins.", reply_markup=back_menu())

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text
    if text.startswith("/"):
        return
    update_user_memory(uid, update.effective_user.username, update.effective_user.first_name, f"text: {text[:30]}")
    try:
        if uid != ADMIN_ID:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"MESSAGE From: {update.effective_user.first_name} @{update.effective_user.username} ({uid}) Msg: {text} Reply: /reply {uid} msg")
    except Exception as e:
        print(e)
    await update.message.reply_text("Thanks! Team will reply soon.", reply_markup=main_menu())

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Only admin.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast msg OR /reply USER_ID msg")
        return
    if context.args[0].isdigit() and update.message.text.startswith("/reply"):
        target_id = int(context.args[0])
        msg = " ".join(context.args[1:])
        try:
            await context.bot.send_message(chat_id=target_id, text=f"Support: {msg}")
            await update.message.reply_text(f"Replied to {target_id}")
        except Exception as e:
            await update.message.reply_text(f"Failed: {e}")
        return
    msg = " ".join(context.args)
    users = get_user_list()
    count = 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=msg, parse_mode="HTML")
            count += 1
        except Exception as e:
            print(e)
    await update.message.reply_text(f"Sent to {count} users")

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=keep_alive_ping, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("reply", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Bot V10.6 FIXED LIVE!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
