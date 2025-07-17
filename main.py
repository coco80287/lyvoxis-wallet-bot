import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv  # ✅ 讀取 .env

load_dotenv()  # ✅ 開始讀取 .env 檔案
TOKEN = os.getenv("BOT_TOKEN")  # ✅ 取出 BOT_TOKEN