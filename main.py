from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "7986353853:AAGFS_F9nPRwRhb6O-53eTNFFdfRGkNcKq0"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🔐 餘額查詢", "💎 VIP 會員"], ["💰 充值", "🏦 提現"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("歡迎使用 LYVOXIS 數位錢包機器人 🪙", reply_markup=reply_markup)

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.run_polling()
