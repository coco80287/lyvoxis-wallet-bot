import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)
from dotenv import load_dotenv

# 載入 .env 設定
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# 日誌設定
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# /start 指令
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("LYVOXIS 錢包已啟動。請選擇功能。")

# 主函式
def main():
    if not TOKEN:
        logger.error("請在 .env 或 Render 環境變數中設定 TELEGRAM_TOKEN")
        return

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    logger.info("Bot 啟動中...")
    application.run_polling()

if __name__ == "__main__":
    main()