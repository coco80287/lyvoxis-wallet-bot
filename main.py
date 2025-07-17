import json
import random
import string
import datetime
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

DATA_FILE = "database.json"

# Load or initialize database
def load_db():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Initialize with basic structure
        db = {"users": {}, "blacklist": []}
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        return db

def save_db():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

db = load_db()

# Multilingual messages
MESSAGES = {
    'en': {
        'choose_language': "Welcome! Please select your language:",
        'language_set': "Your language has been set to English.",
        'bind_button': "Bind Address",
        'bind_success': "Your address has been bound: {address}\nYour balance: {balance} U",
        'already_bound': "You have already bound an address: {address}",
        'no_address': "You need to bind an address first. Please use the Bind Address button.",
        'balance': "📊 Balance Inquiry\nAddress: {address}\nBalance: {balance} U",
        'deposit': "💰 Deposit",
        'deposit_info': "Please send USDT to your address: {address}\n(This is a simulation; your balance will be updated automatically.)",
        'withdraw': "🏦 Withdraw",
        'withdraw_info': "Your withdrawal request has been submitted and is pending manual review.",
        'withdraw_no_address': "You need to bind an address to withdraw.",
        'vip': "👑 VIP Info:\n1. 1-Month Package: 10 U (10% off)\n2. 3-Month Package: 25 U (15% off)\n3. 12-Month Package: 90 U (25% off)",
        'swap': "🔄 Flash Swap",
        'swap_select': "Flash Swap: Select the currency to convert to USDT.",
        'swap_amount': "Enter the amount of {coin} to convert:",
        'swap_result': "Converted {amount} {coin} to {usdt_amount:.2f} U (including 0.5% fee).\nYour new balance: {balance:.2f} U",
        'card': "💳 Virtual Card:",
        'card_info': "Number: {number}\nExpiry: {expiry}\nCVV: {cvv}",
        'topup': "📞 Phone Top-up",
        'topup_phone': "Please enter your phone number.",
        'topup_amount': "Select top-up amount for {phone}:",
        'topup_success': "Phone {phone} has been topped up by {amount} U.\nNew balance: {balance:.2f} U",
        'insufficient': "Insufficient balance for top-up.",
        'blacklisted': "⚠️ Your address is blacklisted. You cannot perform this operation."
    },
    'zh_tw': {
        'choose_language': "歡迎！請選擇語言：",
        'language_set': "您的語言已設置為繁體中文。",
        'bind_button': "綁定地址",
        'bind_success': "您的地址已綁定：{address}\n您的餘額：{balance} U",
        'already_bound': "您已經綁定了地址：{address}",
        'no_address': "您需要先綁定地址。請點擊綁定地址按鈕。",
        'balance': "📊 查詢餘額\n地址：{address}\n餘額：{balance} U",
        'deposit': "💰 充值",
        'deposit_info': "請向以下地址充值 USDT：{address}\n（模擬入金，餘額將自動更新）",
        'withdraw': "🏦 提幣",
        'withdraw_info': "您的提幣申請已提交，將由人工審核。",
        'withdraw_no_address': "您需要綁定地址才能提幣。",
        'vip': "👑 VIP 購買資訊：\n1. 1個月方案：10 U (九折)\n2. 3個月方案：25 U (八五折)\n3. 12個月方案：90 U (七五折)",
        'swap': "🔄 閃兌",
        'swap_select': "閃兌：請選擇要兌換為 USDT 的貨幣。",
        'swap_amount': "請輸入要兌換的 {coin} 數量：",
        'swap_result': "已將 {amount} {coin} 兌換為 {usdt_amount:.2f} U（已扣除0.5%手續費）。\n您的新餘額：{balance:.2f} U",
        'card': "💳 虛擬卡：",
        'card_info': "卡號：{number}\n有效期：{expiry}\nCVV：{cvv}",
        'topup': "📞 手機儲值",
        'topup_phone': "請輸入您的手機號碼。",
        'topup_amount': "請選擇儲值金額（{phone}）：",
        'topup_success': "手機 {phone} 已儲值 {amount} U。\n您的新餘額：{balance:.2f} U",
        'insufficient': "餘額不足，無法儲值。",
        'blacklisted': "⚠️ 您的地址已被列入黑名單，無法執行此操作。"
    },
    'zh_cn': {
        'choose_language': "欢迎！请选择语言：",
        'language_set': "您的语言已设置为简体中文。",
        'bind_button': "绑定地址",
        'bind_success': "您的地址已绑定：{address}\n您的余额：{balance} U",
        'already_bound': "您已经绑定了地址：{address}",
        'no_address': "您需要先绑定地址。请点击绑定地址按钮。",
        'balance': "📊 查询余额\n地址：{address}\n余额：{balance} U",
        'deposit': "💰 充值",
        'deposit_info': "请向以下地址充值 USDT：{address}\n（模拟入金，余额将自动更新）",
        'withdraw': "🏦 提币",
        'withdraw_info': "您的提币申请已提交，将由人工审核。",
        'withdraw_no_address': "您需要绑定地址才能提币。",
        'vip': "👑 VIP 购买信息：\n1. 1个月方案：10 U (九折)\n2. 3个月方案：25 U (八五折)\n3. 12个月方案：90 U (七五折)",
        'swap': "🔄 闪兑",
        'swap_select': "闪兑：请选择要兑换为 USDT 的货币。",
        'swap_amount': "请输入要兑换的 {coin} 数量：",
        'swap_result': "已将 {amount} {coin} 兑换为 {usdt_amount:.2f} U（已扣除0.5%手续费）。\n您的新余额：{balance:.2f} U",
        'card': "💳 虚拟卡：",
        'card_info': "卡号：{number}\n有效期：{expiry}\nCVV：{cvv}",
        'topup': "📞 手机充值",
        'topup_phone': "请输入您的手机号码。",
        'topup_amount': "请选择充值金额（{phone}）：",
        'topup_success': "手机 {phone} 已充值 {amount} U。\n您的新余额：{balance:.2f} U",
        'insufficient': "余额不足，无法充值。",
        'blacklisted': "⚠️ 您的地址已被列入黑名单，无法执行此操作。"
    }
}

# Helper to get user's language or default to English
def get_lang(user_id):
    return db["users"].get(str(user_id), {}).get("lang", "en")

# Helper to get message text
def tr(user_id, key, **kwargs):
    lang = get_lang(user_id)
    text = MESSAGES.get(lang, MESSAGES['en']).get(key, "")
    if kwargs:
        try:
            return text.format(**kwargs)
        except:
            return text
    return text

# Generate main menu keyboard based on language
def main_menu_keyboard(user_id):
    lang = get_lang(user_id)
    keys = MESSAGES[lang]
    btn_balance = KeyboardButton(keys['balance'].split('\n')[0])
    btn_deposit = KeyboardButton(keys['deposit'])
    btn_withdraw = KeyboardButton(keys['withdraw'])
    btn_vip = KeyboardButton(keys['vip'].split('\n')[0])
    btn_swap = KeyboardButton(keys['swap'])
    btn_card = KeyboardButton(keys['card'])
    btn_topup = KeyboardButton(keys['topup'])
    return ReplyKeyboardMarkup(
        [[btn_balance, btn_deposit],
         [btn_withdraw, btn_vip],
         [btn_swap, btn_card],
         [btn_topup]],
        resize_keyboard=True
    )

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("English", callback_data="lang:en")],
        [InlineKeyboardButton("繁體中文", callback_data="lang:zh_tw")],
        [InlineKeyboardButton("简体中文", callback_data="lang:zh_cn")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(MESSAGES['en']['choose_language'], reply_markup=reply_markup)

# Language selection callback
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split(':')
    if len(data) == 2 and data[0] == 'lang':
        lang = data[1]
    else:
        return
    user_id = str(query.from_user.id)
    if user_id not in db["users"]:
        # Initialize new user with default balance and no address
        db["users"][user_id] = {"lang": lang, "address": "", "balance": 100.0}
    else:
        db["users"][user_id]["lang"] = lang
    save_db()
    # Acknowledge language set
    await query.edit_message_text(text=MESSAGES[lang]['language_set'])
    # Provide Bind Address button
    bind_btn = InlineKeyboardButton(MESSAGES[lang]['bind_button'], callback_data="bind")
    await query.message.reply_text(MESSAGES[lang]['bind_button'], reply_markup=InlineKeyboardMarkup([[bind_btn]]))

# Bind address callback
async def bind_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    lang = get_lang(user_id)
    user_data = db["users"].get(user_id)
    if not user_data:
        await query.edit_message_text(MESSAGES[lang]['no_address'])
        return
    if user_data.get("address"):
        text = tr(user_id, 'already_bound', address=user_data["address"])
    else:
        address = f"0x{user_id}ABCDEF"
        db["users"][user_id]["address"] = address
        if "balance" not in db["users"][user_id]:
            db["users"][user_id]["balance"] = 100.0
        save_db()
        text = tr(user_id, 'bind_success', address=address, balance=db["users"][user_id]["balance"])
    await query.edit_message_text(text, reply_markup=main_menu_keyboard(query.from_user.id))

# Balance inquiry handler
async def handle_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user = db["users"].get(user_id)
    if not user or not user.get("address"):
        await update.message.reply_text(tr(user_id, 'no_address'), reply_markup=main_menu_keyboard(update.effective_user.id))
        return
    address = user["address"]
    balance = user.get("balance", 0.0)
    await update.message.reply_text(tr(user_id, 'balance', address=address, balance=balance),
                                    reply_markup=main_menu_keyboard(update.effective_user.id))

# Deposit simulation handler
async def handle_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in db["users"] or not db["users"][user_id].get("address"):
        await update.message.reply_text(tr(user_id, 'no_address'), reply_markup=main_menu_keyboard(update.effective_user.id))
        return
    address = db["users"][user_id]["address"]
    await update.message.reply_text(tr(user_id, 'deposit_info', address=address),
                                    reply_markup=main_menu_keyboard(update.effective_user.id))

# Withdraw request handler
async def handle_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in db["users"] or not db["users"][user_id].get("address"):
        await update.message.reply_text(tr(user_id, 'withdraw_no_address'), reply_markup=main_menu_keyboard(update.effective_user.id))
        return
    address = db["users"][user_id]["address"]
    if address in db.get("blacklist", []):
        await update.message.reply_text(tr(user_id, 'blacklisted'), reply_markup=main_menu_keyboard(update.effective_user.id))
        return
    await update.message.reply_text(tr(user_id, 'withdraw_info'), reply_markup=main_menu_keyboard(update.effective_user.id))

# VIP info handler
async def handle_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    await update.message.reply_text(tr(user_id, 'vip'), reply_markup=main_menu_keyboard(update.effective_user.id))

# Flash Swap currency selection
async def swap_select_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in db["users"]:
        await update.message.reply_text(tr(user_id, 'no_address'), reply_markup=main_menu_keyboard(update.effective_user.id))
        return
    address = db["users"][user_id].get("address", "")
    if address in db.get("blacklist", []):
        await update.message.reply_text(tr(user_id, 'blacklisted'), reply_markup=main_menu_keyboard(update.effective_user.id))
        return
    buttons = [
        [InlineKeyboardButton("ETH", callback_data="swap:ETH"),
         InlineKeyboardButton("BTC", callback_data="swap:BTC"),
         InlineKeyboardButton("TRX", callback_data="swap:TRX")]
    ]
    await update.message.reply_text(tr(user_id, 'swap_select'), reply_markup=InlineKeyboardMarkup(buttons))

# Flash Swap amount prompt
async def swap_currency_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split(':')
    if len(data) != 2 or data[0] != 'swap':
        return
    currency = data[1]
    user_id = str(query.from_user.id)
    context.user_data['swap_currency'] = currency
    await query.edit_message_text(tr(user_id, 'swap_amount', coin=currency))

# Handle swap amount and perform calculation
async def handle_swap_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if 'swap_currency' not in context.user_data:
        return  # Not expecting swap amount
    try:
        amount = float(update.message.text)
    except ValueError:
        await update.message.reply_text("Invalid number.", reply_markup=main_menu_keyboard(update.effective_user.id))
        context.user_data.pop('swap_currency', None)
        return
    user = db["users"].get(user_id)
    if not user or not user.get("address"):
        await update.message.reply_text(tr(user_id, 'no_address'), reply_markup=main_menu_keyboard(update.effective_user.id))
        context.user_data.pop('swap_currency', None)
        return
    if user["address"] in db.get("blacklist", []):
        await update.message.reply_text(tr(user_id, 'blacklisted'), reply_markup=main_menu_keyboard(update.effective_user.id))
        context.user_data.pop('swap_currency', None)
        return
    currency = context.user_data['swap_currency']
    symbol = f"{currency}USDT"
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                price = float(data['price'])
    except Exception as e:
        await update.message.reply_text("Failed to retrieve price.", reply_markup=main_menu_keyboard(update.effective_user.id))
        context.user_data.pop('swap_currency', None)
        return
    usdt_amount = amount * price * 0.995  # after 0.5% fee
    db["users"][user_id]["balance"] = db["users"][user_id].get("balance", 0.0) + usdt_amount
    save_db()
    new_balance = db["users"][user_id]["balance"]
    await update.message.reply_text(
        tr(user_id, 'swap_result', amount=amount, coin=currency, usdt_amount=usdt_amount, balance=new_balance),
        reply_markup=main_menu_keyboard(update.effective_user.id)
    )
    context.user_data.pop('swap_currency', None)

# Virtual card issuance
async def handle_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    card_number = "".join(random.choice(string.digits) for _ in range(16))
    expiry = (datetime.date.today() + datetime.timedelta(days=365*3)).strftime("%m/%y")
    cvv = "".join(random.choice(string.digits) for _ in range(3))
    text = f"{tr(user_id, 'card_info', number=card_number, expiry=expiry, cvv=cvv)}"
    await update.message.reply_text(text, reply_markup=main_menu_keyboard(update.effective_user.id))

# Phone top-up: prompt for phone
async def handle_topup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    await update.message.reply_text(tr(user_id, 'topup_phone'))
    context.user_data['awaiting_phone'] = True

# Handle phone number input
async def handle_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not context.user_data.get('awaiting_phone'):
        return
    phone = update.message.text.strip()
    context.user_data['phone'] = phone
    context.user_data['awaiting_phone'] = False
    amounts = [50, 100, 200, 500]
    buttons = [[InlineKeyboardButton(f"{amt} U", callback_data=f"topup:{amt}")] for amt in amounts]
    await update.message.reply_text(tr(user_id, 'topup_amount', phone=phone), reply_markup=InlineKeyboardMarkup(buttons))

# Handle top-up amount selection
async def handle_topup_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split(':')
    if len(data) != 2 or data[0] != 'topup':
        return
    amount = int(data[1])
    user_id = str(query.from_user.id)
    phone = context.user_data.get('phone', '')
    user = db["users"].get(user_id)
    if not user:
        await query.edit_message_text(tr(user_id, 'no_address'), reply_markup=main_menu_keyboard(query.from_user.id))
        return
    address = user.get("address", "")
    if address in db.get("blacklist", []):
        await query.edit_message_text(tr(user_id, 'blacklisted'), reply_markup=main_menu_keyboard(query.from_user.id))
        return
    balance = user.get("balance", 0.0)
    if balance < amount:
        await query.edit_message_text(tr(user_id, 'insufficient'), reply_markup=main_menu_keyboard(query.from_user.id))
    else:
        new_balance = balance - amount
        db["users"][user_id]["balance"] = new_balance
        save_db()
        text = tr(user_id, 'topup_success', phone=phone, amount=amount, balance=new_balance)
        await query.edit_message_text(text, reply_markup=main_menu_keyboard(query.from_user.id))
    context.user_data.pop('phone', None)

# Generic text handler to route button presses
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text
    user_lang = get_lang(user_id)
    if user_id not in db["users"]:
        return
    if context.user_data.get('swap_currency') is not None:
        await handle_swap_amount(update, context)
        return
    if context.user_data.get('awaiting_phone'):
        await handle_phone_number(update, context)
        return
    keys = MESSAGES[user_lang]
    if text == keys['balance'].split('\n')[0]:
        await handle_balance(update, context)
    elif text == keys['deposit']:
        await handle_deposit(update, context)
    elif text == keys['withdraw']:
        await handle_withdraw(update, context)
    elif text == keys['vip'].split('\n')[0]:
        await handle_vip(update, context)
    elif text == keys['swap']:
        await swap_select_currency(update, context)
    elif text == keys['card']:
        await handle_card(update, context)
    elif text == keys['topup']:
        await handle_topup(update, context)

def main():
    # Replace 'YOUR_BOT_TOKEN' with your Telegram bot token
    TOKEN = "YOUR_BOT_TOKEN"
    application = ApplicationBuilder().token(TOKEN).build()

    # Handlers registration
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(set_language, pattern=r"^lang:"))
    application.add_handler(CallbackQueryHandler(bind_address, pattern=r"^bind"))
    application.add_handler(CallbackQueryHandler(swap_currency_selected, pattern=r"^swap:"))
    application.add_handler(CallbackQueryHandler(handle_topup_amount, pattern=r"^topup:"))
    application.add_handler(MessageHandler(filters.Regex(r'^\d+(\.\d+)?$'), handle_swap_amount))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    application.run_polling()

if __name__ == '__main__':
    main()