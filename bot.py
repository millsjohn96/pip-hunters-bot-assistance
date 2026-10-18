import os
import json
import logging
import threading
import datetime
import glob
import time
import requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# ===== CONFIG =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_1 = "@PipHuntersSignals1"
FREE_CHANNEL_LINK = "https://t.me/PipHuntersSignals1"
DERIV_LINK = "https://t.deriv.link?t=N886WMZM3C76"
BACKUP_CHANNEL = "@PipHuntersSignals2"
USERS_FILE = "users.json"

logging.basicConfig(level=logging.INFO)

# ===== FLASK + ANTI-SLEEP (24/7) =====
flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "Pip Hunters Bot V10.5 FULL FINAL LIVE - 24/7 Anti-Sleep"
@flask_app.route('/health')
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

def keep_alive_ping():
    # Pings itself every 10 minutes so Render never sleeps
    while True:
        time.sleep(600)
        try:
            url = os.getenv("RENDER_EXTERNAL_URL")
            if url:
                requests.get(url, timeout=10)
                print("Keep alive ping sent")
        except Exception as e:
            print(f"Ping failed: {e}")

# ===== USER MEMORY =====
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
        print(f"Load error: {e}")
    return {}

def save_data(data):
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Save error: {e}")

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

# ===== MENUS =====
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

# ===== SEND REAL CHARTS - VIVID LONG =====
async def send_real_charts(chat_id, context, include_ebook_text=False):
    captions = [
        "📊 CHART 1: 14th October - Sweep Model A (BUY Setup)\n\nThis chart shows a classic liquidity sweep. Price first swept below 4070, taking out all early buyers stop losses. After the sweep, we saw strong bullish momentum shifting structure to the upside. The red box at 4129 was our institutional order block entry. Price then rallied aggressively to 4168 which acted as a liquidity magnet. Total move was huge. This is how Smart Money traps retail before the real move. Lesson: Never buy before sweep.",
        "📊 CHART 2: 15th-16th October - Institutional Red Boxes (Key Levels)\n\nThis is M30 timeframe showing two powerful breaker blocks. The market has marked 4129 and 4168 as critical decision points where banks placed orders. Notice how price keeps respecting the 4168 level - it holds as support and resistance multiple times. The red boxes are not random, they are where Smart Money is waiting. When you understand these boxes, you stop chasing price and start waiting at the right zones. Patience is key.",
        "📊 CHART 3: 9th October - Early Morning Rally (Model B)\n\nThis chart captures a beautiful 5:00 AM GMT breakout. Price was consolidating around 4145 during Asian session. Once London kill zone started, price broke structure bullish with strong displacement. The level 4168 which was previously resistance flipped to become solid support. This is what we call Model B - a Breaker Block retest. Many traders missed this because they were sleeping, but our system caught it at the exact entry. London open is powerful.",
        "📊 CHART 4: 6th-7th October - Double Top Reversal (SELL Setup)\n\nPerfect example of a double top failure. Price made two attempts to break 4176 and failed both times, creating equal highs. This is a trap for breakout buyers. After the second rejection, price collapsed aggressively down to 4055, sweeping all weak longs. The breakdown below 4168 confirmed the shift. This chart teaches you why we never buy double tops without confirmation - we wait for the sweep first. Equal highs = liquidity.",
        "📊 CHART 5: 16th October M15 - Intraday Holding & MSS\n\nThis is lower timeframe M15 execution chart from 13:45 to 18:45 on 16th October. After a sharp sell-off, price returned to 4168 and started holding above it. This holding behavior plus a Market Structure Shift (MSS) on M15 gave us a high-probability long entry. You can see how price respects the level for hours. This is real-time proof that institutional levels hold even on volatile days. This is exactly how we time entries."
    ]
    # Try proper names first, then any IMG files
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
        txt = f"📖 PIP HUNTERS E-BOOK + 5 REAL CHARTS\n\nPrice: $100 - FREE Today Only!\n\nInside You Will Learn:\n• How to Identify Institutional Order Blocks\n• The 10-Point Scoring System (7/10 Rule)\n• London & New York Kill Zones Explained\n• $100 to $1000 Growth Blueprint\n• Professional Risk Management\n• 5 REAL MT5 Chart Breakdowns With Vivid Explanation\n\n👇 Below are your 5 REAL MT5 charts with full explanation:\n\nJoin: {FREE_CHANNEL_LINK}\nAccount: {DERIV_LINK}"
        try:
            await context.bot.send_message(chat_id=chat_id, text=txt)
        except:
            pass

    if not found:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Charts are uploading... please try again in 1 minute")
        return

    for idx, fn in enumerate(found):
        try:
            cap = captions[idx] if idx < len(captions) else f"📊 REAL MT5 CHART {idx+1}"
            if os.path.exists(fn):
                with open(fn, 'rb') as photo:
                    await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=cap)
        except Exception as e:
            logging.error(f"Failed {fn}: {e}")
            try:
                await context.bot.send_message(chat_id=chat_id, text=captions[idx] if idx < len(captions) else "Chart")
            except:
                pass

# ===== COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = update.effective_user
    data = load_data()
    is_returning = str(uid) in data
    last_action = get_last_action(uid) if is_returning else "start"
    update_user_memory(uid, user.username, user.first_name, "start")
    # Notify admin
    try:
        if uid != ADMIN_ID:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔔 {'RETURNING' if is_returning else 'NEW'} USER\nName: {user.first_name} @{user.username}\nID: {uid}\nLast: {last_action}\nTotal Users: {len(load_data())}")
    except:
        pass
    name = user.first_name or "Trader"
    if is_returning and last_action != "start":
        resume_map = {"vip": "VIP Access", "signals": "Free Signals", "support": "Support", "about_academy": "About Us", "market": "Market Overview", "education": "Free Education", "live_session": "Live Trading", "ebook": "E-Book", "copytrading": "Copy Trading", "autobot": "Auto Trading Bot", "faq": "FAQ", "risk": "Risk Management"}
        resume_text = resume_map.get(last_action, last_action)
        text = f"Welcome back {name}! 👋\n\nYou left off at: *{resume_text}*\n\nWe saved your place. Continue where you left off?\n\nSelect below:"
    else:
        text = f"Welcome {name} to Pip Hunters\n\nProfessional Forex & Synthetic Indices Signals Provider\nAccuracy: 85-90% | 3-5 Signals Daily\n\nSelect an option below:"
    await update.message.reply_text(text, reply_markup=main_menu())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🆘 Help: /start for menu\nSupport: @PipHuntersSignals2", reply_markup=main_menu())

# ===== BUTTON HANDLER - ALL RESPONSES =====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = query.from_user.id
    update_user_memory(uid, query.from_user.username, query.from_user.first_name, data)
    # Notify admin of click
    try:
        if uid != ADMIN_ID:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"💬 CLICK: {data}\nFrom: {query.from_user.first_name} @{query.from_user.username} ({uid})")
    except:
        pass

    if data in ['main', 'welcome']:
        await query.message.reply_text("📋 Main Menu - Select an option:", reply_markup=main_menu())

    elif data == 'signals':
        await query.message.reply_text(
            f"📈 Free Trading Signals\n\nAll our free signals are posted live in our official channel:\n{FREE_CHANNEL_LINK}\n\nWhat you get:\n• 3-5 high-quality signals daily\n• XAUUSD, Major Forex Pairs & Synthetic Indices\n• Clear Entry, Stop Loss and Take Profit\n• Proper risk to reward\n\nMake sure to enable notifications so you don't miss any signal.",
            reply_markup=back_menu())

    elif data == 'about_academy':
        await query.message.reply_text(
            f"🎓 About Pip Hunters\n\nProfessional trading community established in 2020\n\nWe are specialized in:\n• Smart Money Concept (SMC)\n• Price Action & Liquidity Concepts\n• Technical Analysis & Market Structure\n• Forex & Synthetic Indices\n• Risk Management & Trading Psychology\n• Boom & Crash & Volatility Indices Mastery\n\nWe don't just trade Forex, we trade both Forex and Synthetic Indices with professional institutional approach.\n\nOur Mission: To help traders become consistently profitable with proper education and discipline.\n\nOfficial Channel:\n{FREE_CHANNEL_LINK}\n\n© 2026 Pip Hunters",
            reply_markup=back_menu())

    elif data == 'education':
        await query.message.reply_text(
            "📚 Free Education Hub\n\nBeginner Modules:\n1. Understanding Market Structure\n2. Support & Resistance Mastery\n3. Risk Management Basics\n4. Introduction to Smart Money Concept\n5. Synthetic Indices Basics\n\nAdvanced modules are available for our community members.\n\nWe post daily lessons and chart breakdowns in our channel.",
            reply_markup=back_menu())

    elif data == 'support':
        kb = [[InlineKeyboardButton("💬 Contact Support", url=f"https://t.me/{BACKUP_CHANNEL.replace('@','')}")],[InlineKeyboardButton("⬅️ Back", callback_data='main')]]
        await query.message.reply_text(
            "🆘 Support Center\n\nOur support team is available 24/5 (Monday to Friday)\n\nResponse time: 5-15 minutes\n\nClick below to contact us directly on Telegram.",
            reply_markup=InlineKeyboardMarkup(kb))

    elif data == 'market':
        await query.message.reply_text(
            f"📊 Market Overview\n\nDaily Market Analysis Schedule (GMT):\n• 09:00 - London Session Open\n• 12:00 - Midday Market Update\n• 16:00 - New York Session\n\nAll detailed analysis is posted in our main channel:\n{FREE_CHANNEL_LINK}",
            reply_markup=back_menu())

    elif data == 'vip':
        kb = [[InlineKeyboardButton("1️⃣ Register Account", url=DERIV_LINK)],[InlineKeyboardButton("2️⃣ Verify Registration", callback_data='verify')],[InlineKeyboardButton("⬅️ Back", callback_data='main')]]
        await query.message.reply_text(
            "💎 VIP Access - FREE Membership\n\nVIP Benefits:\n• 5-7 Premium Signals Daily\n• Higher Accuracy & Better Risk to Reward\n• Live Trading Sessions (Coming Soon)\n• Private Education & Mentorship\n• Priority Support\n\nHow to join for FREE:\n1. Create account via button below\n2. Send screenshot of your dashboard HERE (to this bot)\n3. Get activated within 10 minutes",
            reply_markup=InlineKeyboardMarkup(kb))

    elif data == 'live_session':
        await query.message.reply_text(
            f"📹 Live Trading Sessions\n\nWe are preparing to launch our live trading sessions where we break down the market in real-time and answer questions.\n\nProposed Schedule:\n• Tuesdays: 20:00 GMT\n• Thursdays: 20:00 GMT\n\nAll live announcements will be made in our main channel:\n{FREE_CHANNEL_LINK}",
            reply_markup=back_menu())

    elif data == 'ebook':
        await query.message.reply_text("📖 Preparing your E-Book with 5 REAL MT5 Charts...\n\nPlease wait, sending charts now... ⏳", reply_markup=back_menu())
        await send_real_charts(query.message.chat_id, context, include_ebook_text=True)
        await query.message.reply_text(f"✅ E-Book + 5 REAL Charts Sent!\n\nAll charts are REAL from MT5, not drawings\nValue $100 - FREE today\n\nJoin: {FREE_CHANNEL_LINK}", reply_markup=back_menu())

    elif data == 'copytrading':
        await query.message.reply_text(
            "👥 Copy Trading Service\n\nWe are working on launching our professional copy trading service.\n\nPlanned Features:\n• Minimum Capital: $100\n• Fully Automated Copying\n• Full Transparency & Trade History\n• Professional Risk Management\n• Suitable for Forex & Synthetic Indices\n\nThis service is not live yet. We are finalizing the system to ensure safety and profitability.\n\nStay tuned in our main channel for official launch announcement.",
            reply_markup=back_menu())

    elif data == 'autobot':
        await query.message.reply_text(
            "🤖 Auto Trading Bot\n\nWe are currently developing our Gold (XAUUSD) and Synthetic Indices Auto Trading Bot.\n\nFeatures Under Development:\n• 24/5 Automated Trading\n• Tested Institutional Strategy\n• Works on VPS for uninterrupted execution\n• Built-in Risk Management\n\nThis bot is not available for public yet. We are in testing phase.\n\nContact support for early access list.",
            reply_markup=back_menu())

    elif data == 'calendar':
        await query.message.reply_text(
            "🗓️ Economic Calendar\n\nAlways check high-impact news before trading:\n• Visit ForexFactory.com for full calendar\n• Avoid trading 15 minutes before and after RED folder news\n\nWe post daily news reminders in our channel to help you avoid risky times.",
            reply_markup=back_menu())

    elif data == 'faq':
        await query.message.reply_text(
            "❓ Frequently Asked Questions (FAQ)\n\n1️⃣ Are your signals free?\nYes, we provide 3-5 free signals daily in our public Telegram channel. VIP members get additional premium signals.\n\n2️⃣ What is your accuracy rate?\nOur historical accuracy is between 85-90% when traders follow our risk management rules properly. We focus on quality over quantity.\n\n3️⃣ Which markets do you trade?\nWe trade Major Forex Pairs (EURUSD, GBPUSD, XAUUSD) and Synthetic Indices (Volatility Indices, Boom & Crash). Both markets are covered.\n\n4️⃣ Which broker do you recommend?\nWe recommend Deriv for both Forex and Synthetic Indices because of fast execution, low spreads and reliability. Use our official link for full support.\n\n5️⃣ How much do I need to start?\nYou can start with as low as $50-$100, but we recommend $100+ for proper risk management. The key is to risk only 1-2% per trade.\n\n6️⃣ Is VIP really free?\nYes, VIP access is completely free. You just need to create your trading account using our official partner link and send us a screenshot for verification.\n\n7️⃣ Do you offer mentorship or education?\nYes, we provide free education in our channel and detailed private mentorship for our community members. We cover SMC, Price Action and Trading Psychology.\n\n8️⃣ How can I contact support?\nClick the Support button in the menu to chat directly with our team on Telegram. We respond within 5-15 minutes during weekdays.",
            reply_markup=back_menu())

    elif data == 'risk':
        await query.message.reply_text(
            "🛡️ Risk Management\n\nGolden Rules for Long-Term Profitability:\n\n• Risk only 1-2% of your account per trade - This is the most important rule\n• Always use a Stop Loss - Never trade without it\n• Don't overtrade - Quality over quantity\n• Follow minimum 1:2 Risk to Reward ratio\n• Trade with caution and discipline - Avoid emotional decisions\n• Take breaks after 2 losses in a row\n\nRemember: Protecting your capital is more important than making profit. This is not financial advice, trade at your own risk.",
            reply_markup=back_menu())

    elif data == 'verify':
        await query.message.reply_text(
            f"✅ Verification Steps\n\n1. Register here: {DERIV_LINK}\n2. Take screenshot of your Deriv dashboard (show your name/ID)\n3. SEND THAT SCREENSHOT HERE as photo to this bot\n\nOur team verifies manually in 10 mins.",
            reply_markup=back_menu())

    # ===== ADMIN APPROVE / REJECT - THIS IS THE IMPORTANT PART YOU ASKED =====
    elif data.startswith("approve_"):
        target_id = int(data.split("_")[1])
        try:
            await context.bot.send_message(chat_id=target_id, text="✅ Congratulations! You are VERIFIED!\n\n🎉 VIP Access Activated!\n\nYour E-Book and VIP channel access will be sent shortly.\n\nWelcome to Pip Hunters VIP!")
            await query.message.reply_text(f"✅ Approved user {target_id} - VIP activated!")
        except Exception as e:
            
