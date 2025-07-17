import os
import json
import random
import string
import asyncio
import aiohttp
import telegram
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# ========= 初始化 ==========
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

# ========= 多語系 ==========
LANG = {
    # ...（保持您的 LANG 字典）
}

def get_lang(user_id):
    data = load_data()
    return data.get(str(user_id), {}).get("lang", "zh-tw")

def set_lang(user_id, lang):
    data = load_data()
    uid = str(user_id)
    data.setdefault(uid, {})["lang"] = lang
    save_data(data)

MOCK_SWAP_ADDRESS = "TGxxxxxxxxxxxxxxxxxxxx"
BLACKLIST = ["0xBAD123", "0x0000000000BADF00D"]

async def get_binance_rate(a, b):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={a.upper()}{b.upper()}"
    try:
        async with aiohttp.ClientSession() as s:
            js = await (await s.get(url)).json()
            return float(js["price"])
    except:
        return 1.0

def generate_card():
    number = "4000 " + " ".join("".join(random.choices(string.digits, k=4)) for _ in range(3))
    expiry = f"{random.randint(1,12):02d}/{random.randint(26,30)}"
    cvv = "".join(random.choices(string.digits, k=3))
    return number, expiry, cvv

# ========= /start 指令 ==========
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = [[
        InlineKeyboardButton("🇹🇼 繁體中文", callback_data="setlang_zh-tw"),
        InlineKeyboardButton("🇨🇳 简体中文", callback_data="setlang_zh-cn"),
        InlineKeyboardButton("🇺🇸 English", callback_data="setlang_en")
    ]]
    await update.message.reply_text(LANG["lang_select"]["zh-tw"], reply_markup=InlineKeyboardMarkup(kb))

# ========= 主選單 ==========
async def show_menu(chat_id, ctx):
    lang = get_lang(chat_id)
    kb = [
        [InlineKeyboardButton("💰 餘額查詢", callback_data="balance")],
        [InlineKeyboardButton("🔗 綁定地址", callback_data="bind")],
        [InlineKeyboardButton("📥 充值", callback_data="recharge")],
        [InlineKeyboardButton("📤 提幣", callback_data="withdraw")],
        [InlineKeyboardButton("🔁 閃兌", callback_data="swap")],
        [InlineKeyboardButton("💳 開卡中心", callback_data="simcard")],
        [InlineKeyboardButton("📲 電話充值", callback_data="phone")],
        [InlineKeyboardButton("💎 VIP 套餐", callback_data="vip")]
    ]
    await ctx.bot.send_message(chat_id=chat_id, text=LANG["start_msg"][lang], reply_markup=InlineKeyboardMarkup(kb))

# ========= Callback Handler ==========
async def handle_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    data.setdefault(uid, {})
    lang = get_lang(uid)

    if q.data.startswith("setlang_"):
        lang2 = q.data.split("_")[1]
        set_lang(uid, lang2)
        await q.edit_message_text("✅ 語言設定完成")
        await show_menu(uid, ctx)
        save_data(data); return

    if q.data == "bind":
        addr = f"0x{uid[-6:]}ABCDEF"
        data[uid]["address"] = addr
        data[uid]["balance"] = 100.0
        save_data(data)
        await q.edit_message_text(LANG["bind_success"][lang].format(addr), parse_mode="Markdown")
        return

    if q.data == "balance":
        user = data.get(uid, {})
        if "address" not in user:
            await q.edit_message_text(LANG["not_bound"][lang])
        elif user["address"] in BLACKLIST:
            await q.edit_message_text(LANG["blacku"][lang])
        else:
            await q.edit_message_text(LANG["balance"][lang].format(user["address"], user["balance"]), parse_mode="Markdown")
        return

    if q.data == "recharge":
        await q.edit_message_text("📥 請轉入專屬地址模擬充值，餘額將自動更新")
        return

    if q.data == "withdraw":
        if "address" not in data[uid]:
            await q.edit_message_text(LANG["not_bound"][lang]); return
        await q.edit_message_text("📤 出金請等待人工審核，預計 5 分鐘內完成")
        return

    if q.data == "swap":
        btns = [[InlineKeyboardButton(f"{a} → {b}", callback_data=f"do_swap_{a}_{b}")] for a,b in [("ETH","USDT"),("BTC","USDT"),("TRX","USDT")]]
        await q.edit_message_text(LANG["select_swap_pair"][lang], reply_markup=InlineKeyboardMarkup(btns))
        return

    if q.data.startswith("do_swap_"):
        _, a, b = q.data.split("_")
        rate = await get_binance_rate(a, b)
        await q.edit_message_text(
            LANG["swap_confirm"][lang].format(a, b, round(rate*0.995,4), MOCK_SWAP_ADDRESS),
            parse_mode="Markdown")
        return

    if q.data == "simcard":
        num, exp, cvv = generate_card()
        await q.edit_message_text(f"💳 虛擬卡開卡成功！\n卡號：`{num}`\n效期：{exp}\nCVV：{cvv}", parse_mode="Markdown")
        return

    if q.data == "phone":
        await q.edit_message_text("📲 請輸入電話號碼，例如：+886987654321")
        ctx.user_data["awaiting_phone"] = True
        return

    if q.data.startswith("phone_amt_"):
        amt = int(q.data.replace("phone_amt_",""))
        fee = amt * 0.005
        total = amt + fee
        bal = data[uid].get("balance",0.0)
        if bal < total:
            await q.edit_message_text("⚠️ 餘額不足，請先充值")
        else:
            data[uid]["balance"] = bal - total
            save_data(data)
            phone = ctx.user_data.get("phone_number","未知號碼")
            await q.edit_message_text(f"✅ 電話號碼 {phone} 已儲值 {amt} U金（含手續費 0.5%）")
        return

# ========= Message Handler ==========
async def handle_msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    data = load_data()
    data.setdefault(uid, {"balance":100.0})
    save_data(data)
    if ctx.user_data.get("awaiting_phone"):
        ctx.user_data["phone_number"] = update.message.text.strip()
        ctx.user_data["awaiting_phone"] = False
        kb = [[InlineKeyboardButton(f"📲 {x} U金", callback_data=f"phone_amt_{x}")] for x in (50,100,300)]
        await update.message.reply_text("請選擇儲值金額：", reply_markup=InlineKeyboardMarkup(kb))

# ========= 主程式 ==========
async def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise RuntimeError("⚠️ BOT_TOKEN 環境變數未設置")
    print("✅ Telegram Bot Lib Version:", telegram.__version__)

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_cb))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    print("✅ Bot 啟動成功！開始 polling …")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())