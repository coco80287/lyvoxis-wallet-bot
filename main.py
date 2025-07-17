import os
import asyncio
import logging
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    CommandHandler, Updater  # 如果環境為 PTB20.x 需改用 ExtBot+Updater 方案
)
from dotenv import load_dotenv

# 設定日誌等級
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# /start 指令的處理函式
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="機器人已啟動。")

def main():
    load_dotenv()
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        logging.error("請在 .env 或環境變數設定 TELEGRAM_TOKEN")
        return

    application = None
    try:
        # 嘗試建立 Application (可能在 Python 3.13 + PTB20.8 時觸發錯誤)
        application = ApplicationBuilder().token(TOKEN).build()
    except AttributeError as e:
        # 偵測到已知的 Updater 屬性錯誤，切換到備用方案
        logging.warning(
            "偵測到 python-telegram-bot 20.8 在 Python 3.13 的已知錯誤，採用備用 Updater 方案。"
            " 建議改用 Python 3.12 或更新版的 python-telegram-bot。"
        )
        # 使用較舊的 ExtBot + Updater 方式初始化機器人
        bot = Bot(token=TOKEN)
        # note: 這裡使用 asyncio.Queue() 作為更新佇列
        update_queue = asyncio.Queue()
        updater = Updater(bot=bot, update_queue=update_queue)
        dispatcher = updater.dispatcher

        # 註冊指令處理
        dispatcher.add_handler(CommandHandler("start", start))

        # 啟動輪詢
        updater.start_polling()
        # 保持運行直到結束
        updater.idle()
        return

    # 正常情況下，註冊指令處理器
    application.add_handler(CommandHandler("start", start))

    # 啟動非同步輪詢 (會自動處理初始化/關閉等)
    application.run_polling()

if __name__ == "__main__":
    main()