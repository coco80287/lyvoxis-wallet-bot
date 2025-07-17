import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 用來讀取環境變數中的 BOT_TOKEN
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# /start 指令回應
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("你好，這是 LYVOXIS 數位錢包機器人。")

# 主程序
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("🤖 Bot 已啟動！")
    app.run_polling()

if __name__ == "__main__":
    main()