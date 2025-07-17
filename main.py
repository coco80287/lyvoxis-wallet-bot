from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "7986353853:AAGFS_F9nPRwRhb6O-53eTNFFdfRGkNcKq0"  # 你自己的 Bot Token

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("歡迎使用 LYVOXIS 數位錢包機器人 ✨")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("請輸入 /start 開始使用機器人。")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    app.bot.set_my_commands([
        BotCommand("start", "開始使用"),
        BotCommand("help", "說明")
    ])

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()