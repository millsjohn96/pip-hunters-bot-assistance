import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
DERIV_LINK = "https://t.deriv.link?t=N886WMZM3C76"
FREE_CHANNEL = "https://t.me/PipHuntersSignals1"
ADMIN_USERNAME = "@PipHuntersSignals2"

WELCOME_TEXT = """🔥 Welcome to PIP HUNTERS SIGNAL ASSISTANT 🔥

Your #1 Source for Premium Forex & Synthetic Signals
🎯 85-90% Accuracy

👇 Choose from menu:"""

VIP_TEXT = """💎 Get VIP Access
- 5-7 Signals daily
- 95% Accuracy

How to get FREE:
1. Register: https://t.deriv.link?t=N886WMZM3C76
2. Send screenshot here
3. We activate VIP in 10 mins"""

VERIFY_TEXT = """✅ Verify Deriv Registration
1. Register: https://t.deriv.link?t=N886WMZM3C76
2. Screenshot your Deriv dashboard
3. SEND photo here now 👇"""

def main_menu():
    keyboard = [
        [InlineKeyboardButton("👋 Welcome! Start Here", callback_data='welcome')],
        [InlineKeyboardButton("🚀 Join Our Free Channel", url=FREE_CHANNEL)],
        [InlineKeyboardButton("📊 About Our Forex & Synthetic Signals", callback_data='about')],
        [InlineKeyboardButton("🆘 Get Help & Support", callback_data='help')],
        [InlineKeyboardButton("📢 Channel Info & Trading Updates", callback_data='channel_info')],
        [InlineKeyboardButton("📩 Contact Our Team", callback_data='contact')],
        [InlineKeyboardButton("🛡️ Trading Risk Management Tips", callback_data='risk')],
        [InlineKeyboardButton("📝 Register with our trusted broker", url=DERIV_LINK)],
        [InlineKeyboardButton("💎 Get VIP access now", callback_data='vip')],
        [InlineKeyboardButton("✅ Verify Deriv Registration", callback_data='verify')],
    ]
    return InlineKeyboardMarkup(keyboard)

def back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data='main')]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, reply_markup=main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data in ['main','welcome']:
        await query.message.reply_text(WELCOME_TEXT, reply_markup=main_menu())
    elif data == 'about':
        await query.message.reply_text("📈 About: Forex (EURUSD, XAUUSD) + Synthetic (V75, Boom & Crash). Daily 3-5 setups.", reply_markup=back_menu())
    elif data == 'help':
        await query.message.reply_text(f"🆘 Help & Support Contact: {ADMIN_USERNAME}", reply_markup=back_menu())
    elif data == 'channel_info':
        await query.message.reply_text("📢 Channel Info Main: @PipHuntersSignals1 - Posts 9AM, 12PM, 4PM GMT", reply_markup=back_menu())
    elif data == 'contact':
        await query.message.reply_text(f"📩 Contact Our Team Admin: {ADMIN_USERNAME} Email: piphunters1@gmail.com", reply_markup=back_menu())
    elif data == 'risk':
        await query.message.reply_text("🛡️ Risk Management: 1. Risk 1-2% per trade 2. Always use SL 3. Max 3 trades/day", reply_markup=back_menu())
    elif data == 'vip':
        kb = [[InlineKeyboardButton("📝 Register Now", url=DERIV_LINK)],[InlineKeyboardButton("✅ Verify Now", callback_data='verify')],[InlineKeyboardButton("⬅️ Back", callback_data='main')]]
        await query.message.reply_text(VIP_TEXT, reply_markup=InlineKeyboardMarkup(kb))
    elif data == 'verify':
        await query.message.reply_text(VERIFY_TEXT, reply_markup=back_menu())

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✅ Verification submitted! Contact {ADMIN_USERNAME} for fast approval.", reply_markup=main_menu())

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
