import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from dotenv import load_dotenv

# 讀取 .env 檔（Render 可省略，這行也不會影響部署）
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# 設定日誌（可選）
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# /start 指令處理
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ LYVOXIS Wallet 機器人啟動成功")

# 主程式
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()  # ⚠️ 不用 asyncio.run 了

if __name__ == "__main__":
    main()