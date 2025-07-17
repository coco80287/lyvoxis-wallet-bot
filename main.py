import os
import json
import random
import string
import asyncio
import aiohttp
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# ========= [資料庫初始化] ==========
USER_DATA_FILE = "database.json"

def load_data():
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(USER_DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ========= [多語言字典] ==========
LANG = {
    "start_msg": {
        "zh-tw": "👋 歡迎使用 LYVOXIS 錢包！請選擇功能 👇",
        "zh-cn": "👋 欢迎使用 LYVOXIS 钱包！请选择功能 👇",
        "en": "👋 Welcome to LYVOXIS Wallet! Please choose an option 👇"
    },
    "lang_select": {
        "zh-tw": "🌐 請選擇語言",
        "zh-cn": "🌐 请选择语言",
        "en": "🌐 Please select language"
    },
    "bind_success": {
        "zh-tw": "✅ 地址已綁定：`{}`",
        "zh-cn": "✅ 地址已绑定：`{}`",
        "en": "✅ Address bound: `{}`"
    },
    "not_bound": {
        "zh-tw": "⚠️ 尚未綁定地址，請先綁定！",
        "zh-cn": "⚠️ 尚未绑定地址，请先绑定！",
        "en": "⚠️ Address not bound. Please bind first!"
    },
    "balance": {
        "zh-tw": "💰 地址：`{}`\n餘額：{} U金",
        "zh-cn": "💰 地址：`{}`\n余额：{} U金",
        "en": "💰 Address: `{}`\nBalance: {} U-Coin"
    },
    "blacku": {
        "zh-tw": "🚫 此地址被列為風險地址，操作已阻止。",
        "zh-cn": "🚫 此地址被列为风险地址，操作已阻止。",
        "en": "🚫 This address is blacklisted. Action blocked."
    },
    "select_swap_pair": {
        "zh-tw": "請選擇兌換幣種對",
        "zh-cn": "请选择兑换币种对",
        "en": "Select a swap pair"
    },
    "swap_confirm": {
        "zh-tw": "🔁 兌換 {} → {}\n匯率：1:{}\n請轉入地址：\n`{}`",
        "zh-cn": "🔁 兑换 {} → {}\n汇率：1:{}\n请转入地址：\n`{}`",
        "en": "🔁 Swap {} → {}\nRate: 1:{}\nSend to:\n`{}`"
    }
}

def get_lang(user_id):
    data = load_data()
    if str(user_id) in data and "lang" in data[str(user_id)]:
        return data[str(user_id)]["lang"]
    return "zh-tw"  # 預設繁體

def set_lang(user_id, lang):
    data = load_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {}
    data[uid]["lang"] = lang
    save_data(data)