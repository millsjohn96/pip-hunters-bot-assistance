import os, json, threading, requests, time
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
CHANNEL = "@PipHuntersSignals1"
CHANNEL_LINK = "https://t.me/PipHuntersSignals1"
VERIFY_GROUP_ID = os.environ.get("VERIFY_GROUP_ID", "") # e.g. -1001234567890 - Your proofs group
TRUSTED_BROKER_LINK = "https://t.deriv.link?t=N886WMZM3C76"
EBOOK_LINK = "https://pip-hunters-bot.onrender.com/ebook"

user_state = {}
if os.path.exists("user_state.json"):
    try: user_state = json.load(open("user_state.json"))
    except: user_state = {}

pending_signal = {} # For admin approval flow

def save_state():
    try: json.dump(user_state, open("user_state.json", "w"))
    except: pass

def set_state(uid, where):
    user_state.setdefault(str(uid), {})["last"] = where
    user_state[str(uid)]["time"] = time.time()
    save_state()

def get_state(uid):
    return user_state.get(str(uid), {}).get("last", "Main Menu")

def set_awaiting(uid, mode):
    user_state.setdefault(str(uid), {})["awaiting"] = mode
    save_state()

def get_awaiting(uid):
    return user_state.get(str(uid), {}).get("awaiting", None)

def get_gold_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r.get("price", 4145.2))
    except: return 4145.20

def build_signal(symbol, side, entry=None):
    price = get_gold_price() if not entry else float(entry)
    sl = price - 60 if side == "BUY" else price + 60
    tp1 = price + 40 if side == "BUY" else price - 40
    tp2 = price + 80 if side == "BUY" else price - 80
    tp3 = price + 120 if side == "BUY" else price - 120
    msg = f"""🚀 PIP HUNTERS FREE SIGNAL | V11
━━━━━━━━━━━━━━━
📊 {symbol} | {side} | SMC MODEL A
💰 Live: {price:.2f}

📍 Entry: {price:.2f}
🛑 SL: {sl:.2f}
✅ TP1: {tp1:.2f}
✅ TP2: {tp2:.2f}
✅ TP3: {tp3:.2f}

📖 Story: OB 4129 + Sweep 4070 holding ✅
🔗 Broker: {TRUSTED_BROKER_LINK}
📢 {CHANNEL_LINK}
#XAUUSD #SMC"""
    return msg

def main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Free Trading Signals", callback_data="free")],
        [InlineKeyboardButton("📖 Trading E-Book (5 REAL Charts)", callback_data="ebook")],
        [InlineKeyboardButton("💹 Live Trading Sessions", callback_data="live")],
        [InlineKeyboardButton("🔗 Create Trading Account - Deriv", callback_data="verify")],
        [InlineKeyboardButton("ℹ️ About Us - Free Education", callback_data="about")],
        [InlineKeyboardButton("💬 Support", callback_data="support")]
    ])

def admin_kb(price):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"💰 Live XAU: {price:.2f}", callback_data="noop")],
        [InlineKeyboardButton("🚀 Preview XAU BUY", callback_data="ap_XAUUSD_BUY"), InlineKeyboardButton("🔻 Preview XAU SELL", callback_data="ap_XAUUSD_SELL")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main")]
    ])

def approval_kb(symbol, side, entry):
    e_str = str(entry) if entry else "auto"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ YES, POST NOW TO CHANNEL", callback_data=f"approve_{symbol}_{side}_{e_str}")],
        [InlineKeyboardButton("✏️ Edit Price", callback_data=f"edit_{symbol}_{side}"), InlineKeyboardButton("❌ Cancel", callback_data="admin_panel")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    last = get_state(uid)
    wb = f"\n\n👋 Welcome back Boss! You were at: {last}" if str(uid) in user_state and last != "Main Menu" else ""
    text = f"🔥 Welcome to PIP HUNTERS Boss!{wb}\n\n💰 We turn 4129 & 4168 into $$$\n👇 Choose (Only 6 buttons):"
    set_state(uid, "Main Menu")
    set_awaiting(uid, None)
    if update.callback_query: await update.callback_query.edit_message_text(text, reply_markup=main_kb())
    else: await update.message.reply_text(text, reply_markup=main_kb())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer(); uid = q.from_user.id; d = q.data
    
    # ADMIN ONLY CHECK FOR ADMIN PANELS
    is_admin_action = d.startswith("ap_") or d.startswith("approve_") or d.startswith("edit_") or d == "admin_panel" or d == "noop"
    if is_admin_action:
        if ADMIN_ID != 0 and uid != ADMIN_ID:
            await q.edit_message_text("❌ This admin panel appears ONLY to admin! You are not admin Boss!")
            return

    if d == "main": await start(update, context); return
    if d == "noop": return

    if d == "ebook":
        set_state(uid, "E-Book Page")
        txt = "📖 PIP HUNTERS E-BOOK FREE ($100 Value)\n\n✅ Order Block 4129\n✅ Liquidity Sweep 4070\n✅ Double Top 4176\n✅ 5 REAL CHARTS inside\n\n💡 TIP: Create Deriv account with our link to unlock E-Book instantly + Bonuses!"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Create Account to Unlock E-Book", callback_data="verify")],[InlineKeyboardButton("📥 I Already Created - Get E-Book", callback_data="created_account")],[InlineKeyboardButton("🔙 Main Menu", callback_data="main")]])
        await q.edit_message_text(txt, reply_markup=kb)

    elif d == "free":
        set_state(uid, "Free Signals Page")
        txt = f"🚀 FREE SIGNALS CHANNEL\n\n📢 {CHANNEL}\nDaily 1-2 FREE XAUUSD signals\n\nJoin now Boss!"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Join FREE Channel", url=CHANNEL_LINK)],[InlineKeyboardButton("🔙 Main", callback_data="main")]])
        await q.edit_message_text(txt, reply_markup=kb)

    elif d == "live":
        set_state(uid, "Live Trading Page")
        price = get_gold_price()
        txt = f"💹 LIVE TRADING SESSIONS\n\n💰 XAU Now: {price:.2f}\n📅 London 09:00 GMT\n📅 NY 13:30 GMT\n\nLive calls in FREE channel"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Join for Live", url=CHANNEL_LINK)],[InlineKeyboardButton("🔙 Main", callback_data="main")]])
        await q.edit_message_text(txt, reply_markup=kb)

    elif d == "verify":
        set_state(uid, "Create Account Page")
        txt = f"🔗 CREATE TRADING ACCOUNT - DERIV\n\n✅ Official Deriv - Verified by Pip Hunters\n✅ Low Spread XAU + Volatility 75\n✅ MTN MoMo Withdraw Ghana\n\n👇 Step 1: Create account with our link\n👇 Step 2: Upload screenshot proof\n👇 Step 3: Get E-Book + Bonuses instantly!\n\nOfficial Link:\n{TRUSTED_BROKER_LINK}"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Step 1: Create Deriv Account Now", url=TRUSTED_BROKER_LINK)],
            [InlineKeyboardButton("📸 Step 2: I Created Account - Upload Proof & Get E-Book", callback_data="created_account")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="main")]
        ])
        await q.edit_message_text(txt, reply_markup=kb)

    elif d == "created_account":
        set_state(uid, "Awaiting Screenshot Proof")
        set_awaiting(uid, "proof")
        txt = f"📸 PROOF UPLOAD - UNLOCK BENEFITS\n\nGreat Boss! To unlock your benefits:\n\n1️⃣ Create account using this link (if not done):\n{TRUSTED_BROKER_LINK}\n\n2️⃣ Take screenshot of your Deriv dashboard showing account created / email\n\n3️⃣ Upload screenshot HERE as photo (tap 📎 and send photo)\n\n🎁 INSTANT BENEFITS WHEN YOU UPLOAD:\n✅ 📖 E-Book ($100 value)\n✅ 📊 5 REAL Charts Pack\n✅ 🎁 3-Day FREE VIP Signals Trial\n✅ 💹 Live Trading Access\n\n👇 Send screenshot photo now Boss!"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="main")]])
        await q.edit_message_text(txt, reply_markup=kb)

    elif d == "about":
        set_state(uid, "About Page")
        txt = "ℹ️ ABOUT US - PIP HUNTERS\n\n📍 Ghana SMC Traders\nFocus: XAUUSD 4129 & 4168\n\n📚 Free Education inside E-Book\n🎯 Help 10k traders pass prop firms\n\nStarted 2023 | 5000+ members"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("📖 Get Free Education (E-Book)", callback_data="ebook")],[InlineKeyboardButton("🔙 Main", callback_data="main")]])
        await q.edit_message_text(txt, reply_markup=kb)

    elif d == "support":
        set_state(uid, "Support Page")
        txt = "💬 SUPPORT\n\n👤 @PipHuntersAdmin\n⏱️ Reply in 5 mins"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("💬 Chat Admin", url="https://t.me/PipHuntersAdmin")],[InlineKeyboardButton("🔙 Main", callback_data="main")]])
        await q.edit_message_text(txt, reply_markup=kb)

    elif d.startswith("ap_"):
        # PREVIEW FLOW - ONLY FOR ADMIN
        _, sym, side = d.split("_")
        price = get_gold_price()
        msg = build_signal(sym, side)
        pending_signal[str(uid)] = {"symbol": sym, "side": side, "entry": None, "msg": msg}
        txt = f"🔐 ADMIN PREVIEW - ONLY YOU CAN SEE THIS\n\n💰 Live Price: {price:.2f}\n\nPreview to post:\n\n{msg}\n\n👇 Approve to post to {CHANNEL}?"
        await q.edit_message_text(txt, reply_markup=approval_kb(sym, side, "auto"))

    elif d.startswith("approve_"):
        # FINAL POST AFTER ADMIN APPROVAL
        try:
            _, sym, side, e_str = d.split("_")
            entry = None if e_str == "auto" else e_str
            msg = build_signal(sym, side, entry)
            await context.bot.send_message(chat_id=CHANNEL, text=msg)
            await q.edit_message_text(f"✅ POSTED to {CHANNEL}!\n\n{msg}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel")]]))
            pending_signal.pop(str(uid), None)
        except Exception as e:
            await q.edit_message_text(f"❌ Failed: {e}\nMake bot ADMIN in {CHANNEL}")

    elif d == "admin_panel":
        await admin_cmd(update, context)

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if get_awaiting(uid) != "proof":
        return # Ignore random photos
    
    # User uploaded proof!
    user = update.effective_user
    username = f"@{user.username}" if user.username else f"{user.first_name}"
    
    # 1. Forward to verification group (if set)
    caption_for_group = f"🚨 NEW DERIV PROOF! V11\n\n👤 User: {username}\n🆔 ID: {uid}\n📅 {time.strftime('%Y-%m-%d %H:%M')}\n✅ Check Deriv affiliate dashboard: https://t.deriv.link?t=N886WMZM3C76\n📖 User unlocked E-Book + Bonuses\n\nAction: Verify in Deriv & Mark as Converted"
    try:
        if VERIFY_GROUP_ID:
            await context.bot.send_photo(chat_id=VERIFY_GROUP_ID, photo=update.message.photo[-1].file_id, caption=caption_for_group)
    except Exception as e:
        print(f"Verify group send failed: {e} - Set VERIFY_GROUP_ID env var")

    # 2. Give benefits instantly to user
    set_awaiting(uid, None)
    set_state(uid, "Benefits Unlocked")
    
    benefits_text = f"""✅ PROOF RECEIVED Boss! Benefits Unlocked! 🎉

Thank you {user.first_name}! Screenshot sent to admin for verification.

🎁 YOUR INSTANT BENEFITS:

1️⃣ 📖 E-BOOK ($100 Value):
{EBOOK_LINK}

2️⃣ 📊 5 REAL CHARTS Pack:
Inside E-Book page 15-20

3️⃣ 🎁 3-Day FREE VIP Signals Trial:
You will get 3 signals daily for 3 days in DM!

4️⃣ 💹 Live Trading Access:
Join {CHANNEL_LINK}

📸 Your proof is being verified in our system. Once verified in Deriv dashboard (24h), you get permanent VIP discount!

💬 Questions? @PipHuntersAdmin

🔙 Tap Main Menu to continue"""

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Download E-Book Now", url=EBOOK_LINK)],
        [InlineKeyboardButton("🚀 Join FREE Channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main")]
    ])
    
    await update.message.reply_text(benefits_text, reply_markup=kb)

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id if update.effective_user else 0
    is_cb = update.callback_query is not None
    if ADMIN_ID != 0 and uid != ADMIN_ID:
        if is_cb: await update.callback_query.edit_message_text("❌ ADMIN ONLY - This panel appears ONLY to you Boss! Set ADMIN_ID in Render ENV")
        else: await update.message.reply_text("❌ ADMIN ONLY - This panel appears ONLY to you Boss!")
        return
    price = get_gold_price()
    txt = f"🔐 ADMIN PANEL V11 - ONLY YOU SEE THIS\n\n💰 Live XAU: {price:.2f}\n📢 {CHANNEL}\n👥 Verify Group: {VERIFY_GROUP_ID if VERIFY_GROUP_ID else 'Not set (set VERIFY_GROUP_ID env)'}\n\n👇 Tap to PREVIEW (not post yet):"
    kb = admin_kb(price)
    if is_cb: await update.callback_query.edit_message_text(txt, reply_markup=kb)
    else: await update.message.reply_text(txt, reply_markup=kb)

async def qs_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if ADMIN_ID != 0 and uid != ADMIN_ID: await update.message.reply_text("❌ ADMIN ONLY - Only you can use this!"); return
    args = context.args
    if not args: await update.message.reply_text("Usage: /qs XAUUSD BUY [price]\nExample: /qs XAUUSD BUY\nThen you approve before posting"); return
    sym = args[0].upper(); side = args[1].upper() if len(args) > 1 else "BUY"; entry = args[2] if len(args) > 2 else None
    price = get_gold_price() if not entry else float(entry)
    msg = build_signal(sym, side, entry)
    pending_signal[str(uid)] = {"symbol": sym, "side": side, "entry": entry, "msg": msg}
    txt = f"🔐 ADMIN PREVIEW - ONLY YOU SEE THIS\n💰 Live: {price}\n\nPreview:\n\n{msg}\n\n👇 Approve?"
    await update.message.reply_text(txt, reply_markup=approval_kb(sym, side, entry if entry else "auto"))

app = Flask(__name__)
@app.route('/')
def home(): return "V11 APPROVAL + SCREENSHOT BENEFITS LIVE - Only admin sees panels"
@app.route('/ebook')
def ebook(): return f"<h1>📖 Pip Hunters E-Book FREE</h1><p>Value $100</p><p>5 REAL Charts inside</p><p><a href='{TRUSTED_BROKER_LINK}'>Create Deriv Account with our link to unlock</a></p><a href='https://t.me/PipHuntersBot'>Get via bot</a>"
@app.route('/verify')
def verify(): return f"<meta http-equiv='refresh' content='0; url={TRUSTED_BROKER_LINK}'><h1>Redirecting to Official Deriv...</h1><a href='{TRUSTED_BROKER_LINK}'>Click if not redirected</a>"

def run_flask(): app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
def main():
    threading.Thread(target=run_flask, daemon=True).start()
    if not TOKEN: print("BOT_TOKEN missing"); return
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_cmd))
    application.add_handler(CommandHandler("qs", qs_cmd))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    print("V11 Starting - Approval + Screenshot Benefits")
    application.run_polling()
if __name__ == "__main__": main()
