import telegram
print("✅ Telegram Bot Lib Version:", telegram.__version__)
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

# === 語言與提示 ===
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
    return "zh-tw"

def set_lang(user_id, lang):
    data = load_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {}
    data[uid]["lang"] = lang
    save_data(data)

MOCK_SWAP_ADDRESS = "TGxxxxxxxxxxxxxxxxxxxx"
BLACKLIST = ["0xBAD123", "0x0000000000BADF00D"]

async def get_binance_rate(from_symbol, to_symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={from_symbol.upper()}{to_symbol.upper()}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                data = await res.json()
                return float(data["price"])
    except:
        return 1.0

def generate_card():
    number = "4000 " + " ".join(["".join(random.choices(string.digits, k=4)) for _ in range(3)])
    expiry = f"{random.randint(1,12):02d}/{random.randint(26,30)}"
    cvv = "".join(random.choices(string.digits, k=3))
    return number, expiry, cvv

# === 回傳 /start 主選單 ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("🇹🇼 繁體中文", callback_data="setlang_zh-tw"),
        InlineKeyboardButton("🇨🇳 简体中文", callback_data="setlang_zh-cn"),
        InlineKeyboardButton("🇺🇸 English", callback_data="setlang_en")
    ]]
    await update.message.reply_text(LANG["lang_select"]["zh-tw"], reply_markup=InlineKeyboardMarkup(keyboard))

# === 主選單 ===
async def show_menu(update, context, user_id):
    lang = get_lang(user_id)
    keyboard = [
        [InlineKeyboardButton("💰 餘額查詢", callback_data="balance")],
        [InlineKeyboardButton("🔗 綁定地址", callback_data="bind")],
        [InlineKeyboardButton("📥 充值", callback_data="recharge")],
        [InlineKeyboardButton("📤 提幣", callback_data="withdraw")],
        [InlineKeyboardButton("🔁 閃兌", callback_data="swap")],
        [InlineKeyboardButton("💳 開卡中心", callback_data="simcard")],
        [InlineKeyboardButton("📲 電話充值", callback_data="phone")],
        [InlineKeyboardButton("💎 VIP 套餐", callback_data="vip")]
    ]
    await context.bot.send_message(chat_id=user_id, text=LANG["start_msg"][lang], reply_markup=InlineKeyboardMarkup(keyboard))

# === Callback Query Handler ===
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    data = load_data()
    lang = get_lang(user_id)

    if user_id not in data:
        data[user_id] = {}

    if query.data.startswith("setlang_"):
        chosen = query.data.replace("setlang_", "")
        set_lang(user_id, chosen)
        await query.edit_message_text("✅ 語言設定完成")
        await show_menu(update, context, user_id)
        return

    if query.data == "bind":
        addr = f"0x{user_id[-6:]}ABCDEF"
        data[user_id]["address"] = addr
        data[user_id]["balance"] = 100.0
        save_data(data)
        await query.edit_message_text(LANG["bind_success"][lang].format(addr), parse_mode="Markdown")

    elif query.data == "balance":
        if "address" not in data[user_id]:
            await query.edit_message_text(LANG["not_bound"][lang])
            return
        if data[user_id]["address"] in BLACKLIST:
            await query.edit_message_text(LANG["blacku"][lang])
            return
        await query.edit_message_text(LANG["balance"][lang].format(data[user_id]["address"], data[user_id]["balance"]), parse_mode="Markdown")

    elif query.data == "recharge":
        await query.edit_message_text("📥 請轉入專屬地址模擬充值，餘額將自動更新")

    elif query.data == "withdraw":
        if "address" not in data[user_id]:
            await query.edit_message_text(LANG["not_bound"][lang])
            return
        await query.edit_message_text("📤 出金請等待人工審核，預計 5 分鐘內完成")

    elif query.data == "vip":
        await query.edit_message_text("💎 VIP 價格：3個月12.9、6個月16.9、12個月29.9\nVIP 可享抽成降至 0.2%")

    elif query.data == "swap":
        btns = [
            [InlineKeyboardButton("ETH → USDT", callback_data="do_swap_ETH_USDT")],
            [InlineKeyboardButton("BTC → USDT", callback_data="do_swap_BTC_USDT")],
            [InlineKeyboardButton("TRX → USDT", callback_data="do_swap_TRX_USDT")]
        ]
        await query.edit_message_text(LANG["select_swap_pair"][lang], reply_markup=InlineKeyboardMarkup(btns))

    elif query.data.startswith("do_swap_"):
        _, from_token, to_token = query.data.split("_")
        rate = await get_binance_rate(from_token, to_token)
        real_rate = round(rate * 0.995, 4)
        await query.edit_message_text(LANG["swap_confirm"][lang].format(from_token, to_token, real_rate, MOCK_SWAP_ADDRESS), parse_mode="Markdown")

    elif query.data == "simcard":
        number, expiry, cvv = generate_card()
        await query.edit_message_text(f"💳 虛擬卡開卡成功！\n卡號：`{number}`\n效期：{expiry}\nCVV：{cvv}", parse_mode="Markdown")

    elif query.data == "phone":
        await query.edit_message_text("📲 請輸入電話號碼，例如：+886987654321")
        context.user_data["awaiting_phone"] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    lang = get_lang(user_id)

    if user_id not in data:
        data[user_id] = {"balance": 100.0}
        save_data(data)

    text = update.message.text.strip()

    if context.user_data.get("awaiting_phone"):
        context.user_data["phone_number"] = text
        context.user_data["awaiting_phone"] = False
        context.user_data["awaiting_amount"] = True

        keyboard = [
            [InlineKeyboardButton("📲 50 U金", callback_data="phone_amt_50")],
            [InlineKeyboardButton("📲 100 U金", callback_data="phone_amt_100")],
            [InlineKeyboardButton("📲 300 U金", callback_data="phone_amt_300")]
        ]
        await update.message.reply_text("請選擇儲值金額：", reply_markup=InlineKeyboardMarkup(keyboard))

async def phone_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    data = load_data()
    lang = get_lang(user_id)

    amt = int(query.data.replace("phone_amt_", ""))
    fee = amt * 0.005
    total = amt + fee
    balance = data[user_id].get("balance", 0.0)

    if balance < total:
        await query.edit_message_text("⚠️ 餘額不足，請先充值")
        return

    data[user_id]["balance"] -= total
    save_data(data)

    phone = context.user_data.get("phone_number", "未知號碼")
    await query.edit_message_text(f"✅ 電話號碼 {phone} 已儲值 {amt} U金（含手續費 0.5%）")

# ========== 主程序 ==========
async def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("⚠️ 請設置 BOT_TOKEN 環境變數")

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback, pattern="^(?!phone_amt_).+"))
    application.add_handler(CallbackQueryHandler(phone_amount_handler, pattern="^phone_amt_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot 啟動成功！")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())