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
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# 模擬資料庫
user_data = {}

# 設定日誌
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 多語系
LANGUAGE_TEXT = {
    'start': {
        'zh_tw': "歡迎使用 LYVOXIS Wallet 多幣種錢包服務，請選擇功能👇",
        'zh_cn': "欢迎使用 LYVOXIS Wallet 多币种钱包服务，请选择功能👇",
        'en': "Welcome to LYVOXIS Wallet. Please choose a function 👇",
    },
    'menu': {
        'zh_tw': ["💰 查詢餘額", "📥 充值", "📤 提領", "🌐 閃兌", "👑 VIP 會員", "📲 客服支援"],
        'zh_cn': ["💰 查询余额", "📥 充值", "📤 提现", "🌐 闪兑", "👑 VIP 会员", "📲 客服支持"],
        'en': ["💰 Balance", "📥 Deposit", "📤 Withdraw", "🌐 Swap", "👑 VIP", "📲 Support"],
    }
}

# 初始語言選擇
LANG_SELECT = InlineKeyboardMarkup([
    [InlineKeyboardButton("繁體中文", callback_data="lang_zh_tw")],
    [InlineKeyboardButton("简体中文", callback_data="lang_zh_cn")],
    [InlineKeyboardButton("English", callback_data="lang_en")],
])

def get_lang(user_id):
    return user_data.get(user_id, {}).get("lang", "zh_tw")

def get_text(key, user_id):
    lang = get_lang(user_id)
    return LANGUAGE_TEXT.get(key, {}).get(lang, "")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {}
    if "lang" not in user_data[user_id]:
        await update.message.reply_text("請選擇語言 / Please select your language", reply_markup=LANG_SELECT)
    else:
        await send_main_menu(update, context)

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = get_text('start', user_id)
    buttons = [[InlineKeyboardButton(btn, callback_data=f"menu_{i}")] for i, btn in enumerate(get_text('menu', user_id))]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def handle_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_code = query.data.replace("lang_", "")
    user_id = query.from_user.id
    user_data[user_id]["lang"] = lang_code
    await query.message.delete()
    await query.message.reply_text(get_text("start", user_id), reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton(btn, callback_data=f"menu_{i}")] for i, btn in enumerate(get_text('menu', user_id))]
    ))

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    index = int(query.data.replace("menu_", ""))
    functions = ["查詢餘額功能", "充值功能", "提領功能", "閃兌功能", "VIP 會員功能", "客服支援功能"]
    await query.message.reply_text(f"👉 {get_text('menu', user_id)[index]}：{functions[index]}（功能建置中）")

async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("請使用下方按鈕選擇功能 🙏")

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_lang, pattern="^lang_"))
    application.add_handler(CallbackQueryHandler(handle_menu, pattern="^menu_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))
    application.run_polling()

if __name__ == "__main__":
    main()