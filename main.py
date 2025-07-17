import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# /start 指令處理器
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 餘額查詢", callback_data="balance")],
        [InlineKeyboardButton("🔗 綁定地址", callback_data="bind")],
        [InlineKeyboardButton("📥 充值", callback_data="deposit")],
        [InlineKeyboardButton("📤 提幣", callback_data="withdraw")],
        [InlineKeyboardButton("🧧 紅包", callback_data="redpacket")],
        [InlineKeyboardButton("💎 VIP", callback_data="vip")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("歡迎使用 LYVOXIS 錢包機器人，請選擇功能 👇", reply_markup=reply_markup)

# 建立 Bot 應用程式
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

# 開始執行
if __name__ == "__main__":
    app.run_polling()