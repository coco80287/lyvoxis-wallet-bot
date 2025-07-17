import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    CommandHandler, CallbackQueryHandler
)

# 載入 .env 中的環境變數
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# /start 指令回應
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

# 處理按鈕點擊
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"你點選了功能：{query.data}")

# 啟動 Bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot 啟動中...")
    app.run_polling()