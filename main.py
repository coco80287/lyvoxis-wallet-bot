import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

# 載入 .env 的環境變數
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# 設定 log
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 指令 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ LYVOXIS 錢包啟動成功")

def main():
    if not TOKEN:
        logger.error("❌ 請在 .env 或 Render 環境變數中設定 TELEGRAM_TOKEN")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    logger.info("✅ Bot 正在啟動...")
    app.run_polling()

if __name__ == "__main__":
    main()