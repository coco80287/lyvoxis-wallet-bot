import os
import random
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters
)

# 模擬資料存儲（可替換為真實資料庫）
BLACKLIST = {"0xBADADDRESS"}  # 範例黑名單地址
DEPOSIT_ADDRESSES = {
    "ETH": "0x1111222233334444555566667777888899990000",
    "BTC": "1BitcoinFakeAddress1234567890",
    "TRX": "TXXXXXXXXXXXXXXXXXXXX"
}

# 多語言訊息模板
TEXT = {
    "choose_language": {
        "TW": "請選擇語言 / Please choose a language",
        "CN": "请选择语言 / Please choose a language",
        "EN": "Please choose a language"
    },
    "language_set": {
        "TW": "已設定語言：繁體中文",
        "CN": "已设置语言：简体中文",
        "EN": "Language set to English"
    },
    "address_created": {
        "TW": "已為您生成地址：{address}",
        "CN": "已为您生成地址：{address}",
        "EN": "Your new address is: {address}"
    },
    "address_exists": {
        "TW": "您的綁定地址為：{address}",
        "CN": "您的绑定地址为：{address}",
        "EN": "Your bound address is: {address}"
    },
    "balance": {
        "TW": "地址 {address} 的餘額為：{balance:.2f} USDT",
        "CN": "地址 {address} 的余额为：{balance:.2f} USDT",
        "EN": "Balance for address {address}: {balance:.2f} USDT"
    },
    "balance_blacklisted": {
        "TW": "您的地址在黑名單中，無法查詢餘額。",
        "CN": "您的地址在黑名单中，无法查询余额。",
        "EN": "Your address is in blacklist, balance query forbidden."
    },
    "deposit_prompt": {
        "TW": "請將資金轉入以下地址：\n{address}",
        "CN": "请将资金转入以下地址：\n{address}",
        "EN": "Please deposit funds to the following address:\n{address}"
    },
    "withdraw_prompt": {
        "TW": "您的提幣申請已提交，請等待人工審核。",
        "CN": "您的提币申请已提交，请等待人工审核。",
        "EN": "Your withdrawal request has been submitted for manual review."
    },
    "withdraw_blacklisted": {
        "TW": "您的地址在黑名單中，無法提幣。",
        "CN": "您的地址在黑名单中，无法提币。",
        "EN": "Your address is in blacklist, withdrawal forbidden."
    },
    "withdraw_insufficient": {
        "TW": "餘額不足，無法提幣。",
        "CN": "余额不足，无法提币。",
        "EN": "Insufficient balance, cannot withdraw."
    },
    "vip_info": {
        "TW": "VIP 套餐：\n3個月 - 價格 $100 (手續費優惠10%)\n6個月 - 價格 $180 (手續費優惠20%)\n12個月 - 價格 $300 (手續費優惠30%)",
        "CN": "VIP 套餐：\n3个月 - 价格 $100 (手续费优惠10%)\n6个月 - 价格 $180 (手续费优惠20%)\n12个月 - 价格 $300 (手续费优惠30%)",
        "EN": "VIP Packages:\n3 months - Price $100 (10% fee discount)\n6 months - Price $180 (20% fee discount)\n12 months - Price $300 (30% fee discount)"
    },
    "exchange_select": {
        "TW": "請選擇您要閃兌的幣種：",
        "CN": "请选择您要闪兑的币种：",
        "EN": "Select the coin to exchange:"
    },
    "exchange_enter_amount": {
        "TW": "請輸入要轉換的 {coin} 金額：",
        "CN": "请输入要转换的 {coin} 数量：",
        "EN": "Enter amount of {coin} to convert:"
    },
    "exchange_result": {
        "TW": "當前匯率：1 {coin} = {price:.2f} USDT\n抽成0.5%後，您將收到約 {amount:.2f} USDT。\n請將 {coin} 發送到地址：\n{address}",
        "CN": "当前汇率：1 {coin} = {price:.2f} USDT\n抽成0.5%後，您将收到约 {amount:.2f} USDT。\n请将 {coin} 转账到地址：\n{address}",
        "EN": "Current rate: 1 {coin} = {price:.2f} USDT\nAfter 0.5% fee, you will receive ~{amount:.2f} USDT.\nPlease send {coin} to address:\n{address}"
    },
    "card_info": {
        "TW": "虛擬信用卡資訊：\n卡號：{number}\n效期：{expiry}\nCVV：{cvv}",
        "CN": "虚拟信用卡信息：\n卡号：{number}\n有效期：{expiry}\nCVV：{cvv}",
        "EN": "Virtual Card Information:\nCard Number: {number}\nExpiry Date: {expiry}\nCVV: {cvv}"
    },
    "topup_ask_phone": {
        "TW": "請輸入要充值的手機號碼：",
        "CN": "请输入要充值的手机号码：",
        "EN": "Please enter the phone number to top up:"
    },
    "topup_select_amount": {
        "TW": "請選擇儲值金額：",
        "CN": "请选择充值金额：",
        "EN": "Select top-up amount:"
    },
    "topup_success": {
        "TW": "手機號碼 {phone} 充值成功，金額 {amount:.2f} 已扣除。",
        "CN": "手机号码 {phone} 充值成功，金额 {amount:.2f} 已扣除。",
        "EN": "Phone number {phone} top-up successful, amount {amount:.2f} has been deducted."
    },
    "insufficient_balance": {
        "TW": "餘額不足！",
        "CN": "余额不足！",
        "EN": "Insufficient balance!"
    }
}

# 定義會話狀態常數
EXCHANGE_COIN, EXCHANGE_AMOUNT = range(2)
TOPUP_PHONE, TOPUP_AMOUNT = range(2)

def get_text(key, lang, **kwargs):
    """取得指定語言對應的文字並格式化。"""
    return TEXT.get(key, {}).get(lang, '').format(**kwargs)

# /start 指令處理：請使用者選擇語言
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("繁體中文", callback_data='lang_TW'),
         InlineKeyboardButton("简体中文", callback_data='lang_CN'),
         InlineKeyboardButton("English", callback_data='lang_EN')]
    ]
    await update.message.reply_text(
        TEXT["choose_language"]["EN"],  # 初始預設英文提示
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 語言按鈕回調：設定使用者語言並生成地址
async def lang_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data  # 例如 "lang_TW"
    lang = data.split("_")[1]
    context.user_data['lang'] = lang
    # 如果沒有地址則創建新地址
    if 'address' not in context.user_data:
        addr = "0x" + ''.join(random.choices('0123456789ABCDEF', k=40))
        context.user_data['address'] = addr
        context.user_data['balance'] = 0.0
        text = get_text("address_created", lang, address=addr)
    else:
        addr = context.user_data['address']
        text = get_text("address_exists", lang, address=addr)
    text_lang = get_text("language_set", lang)
    # 更新訊息為語言設定及地址訊息
    await query.edit_message_text(text_lang + "\n" + text)

# /address 指令：顯示或生成地址
async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    lang = user_data.get('lang', 'EN')
    if 'address' not in user_data:
        addr = "0x" + ''.join(random.choices('0123456789ABCDEF', k=40))
        user_data['address'] = addr
        user_data['balance'] = 0.0
        msg = get_text("address_created", lang, address=addr)
    else:
        addr = user_data['address']
        msg = get_text("address_exists", lang, address=addr)
    await update.message.reply_text(msg)

# /balance 指令：查詢餘額
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    lang = user_data.get('lang', 'EN')
    # 如果沒有地址則自動創建
    if 'address' not in user_data:
        addr = "0x" + ''.join(random.choices('0123456789ABCDEF', k=40))
        user_data['address'] = addr
        user_data['balance'] = 0.0
        await update.message.reply_text(get_text("address_created", lang, address=addr))
        return
    addr = user_data['address']
    # 黑名單檢查
    if addr in BLACKLIST:
        await update.message.reply_text(get_text("balance_blacklisted", lang))
        return
    bal = user_data.get('balance', 0.0)
    await update.message.reply_text(get_text("balance", lang, address=addr, balance=bal))

# /deposit 指令：顯示充值地址
async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    lang = user_data.get('lang', 'EN')
    if 'address' not in user_data:
        addr = "0x" + ''.join(random.choices('0123456789ABCDEF', k=40))
        user_data['address'] = addr
        user_data['balance'] = 0.0
    addr = user_data['address']
    await update.message.reply_text(get_text("deposit_prompt", lang, address=addr))

# /withdraw 指令：模擬提幣請求
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    lang = user_data.get('lang', 'EN')
    if 'address' not in user_data:
        await update.message.reply_text(get_text("address_exists", lang, address=""))
        return
    addr = user_data['address']
    if addr in BLACKLIST:
        await update.message.reply_text(get_text("withdraw_blacklisted", lang))
        return
    args = context.args
    if not args or not args[0].replace('.', '').isdigit():
        await update.message.reply_text("Usage: /withdraw <amount>")
        return
    amount = float(args[0])
    balance = user_data.get('balance', 0.0)
    if amount > balance:
        await update.message.reply_text(get_text("withdraw_insufficient", lang))
        return
    # 扣除餘額並顯示提交訊息
    user_data['balance'] = balance - amount
    await update.message.reply_text(get_text("withdraw_prompt", lang))

# /vip 指令：顯示 VIP 套餐資訊
async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    lang = user_data.get('lang', 'EN')
    await update.message.reply_text(get_text("vip_info", lang))

# /exchange 指令：開始閃兌流程（對話）
async def exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    lang = user_data.get('lang', 'EN')
    keyboard = [
        [InlineKeyboardButton("ETH", callback_data='coin_ETH'),
         InlineKeyboardButton("BTC", callback_data='coin_BTC'),
         InlineKeyboardButton("TRX", callback_data='coin_TRX')]
    ]
    await update.message.reply_text(
        get_text("exchange_select", lang),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return EXCHANGE_COIN

async def exchange_coin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data  # 例如 "coin_ETH"
    coin = data.split("_")[1]
    context.user_data['exchange_coin'] = coin
    lang = context.user_data.get('lang', 'EN')
    text = get_text("exchange_enter_amount", lang, coin=coin)
    await query.edit_message_text(text)
    return EXCHANGE_AMOUNT

async def exchange_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    lang = user_data.get('lang', 'EN')
    coin = user_data.get('exchange_coin')
    if not coin:
        await update.message.reply_text(get_text("exchange_select", lang))
        return ConversationHandler.END
    try:
        amt = float(update.message.text)
    except ValueError:
        await update.message.reply_text("Invalid amount.")
        return ConversationHandler.END
    # 呼叫 Binance API 取得即時匯率 [oai_citation:6‡developers.binance.com](https://developers.binance.com/docs/binance-spot-api-docs/faqs/market_data_only#:~:text=,GET%20%2Fapi%2Fv3%2Ftime)
    symbol = coin + "USDT"
    price = 0.0
    try:
        res = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}')
        data = res.json()
        price = float(data.get('price', 0))
    except Exception:
        pass
    received = amt * price * 0.995  # 扣除 0.5% 抽成
    address = DEPOSIT_ADDRESSES.get(coin, '')
    text = get_text("exchange_result", lang,
                    coin=coin, price=price, amount=received, address=address)
    await update.message.reply_text(text)
    return ConversationHandler.END

# /card 指令：生成虛擬信用卡資訊
async def card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    lang = user_data.get('lang', 'EN')
    # 生成前15位隨機數字，並計算 Luhn 校驗碼 [oai_citation:7‡github.com](https://github.com/wcDogg/python-cc-num-gen#:~:text=,with%20CVV%20and%20expiration%20dates)
    def luhn_checksum(num_str):
        digits = [int(d) for d in num_str]
        for i in range(len(digits)-2, -1, -2):
            doubled = digits[i] * 2
            if doubled > 9:
                doubled -= 9
            digits[i] = doubled
        return sum(digits) % 10
    first15 = ''.join(random.choices('0123456789', k=15))
    checksum = (10 - luhn_checksum(first15 + '0')) % 10
    card_num = first15 + str(checksum)
    year = datetime.now().year + random.randint(1,3)
    month = random.randint(1,12)
    expiry = f"{month:02d}/{str(year)[-2:]}"
    cvv = ''.join(random.choices('0123456789', k=3))
    text = get_text("card_info", lang, number=card_num, expiry=expiry, cvv=cvv)
    await update.message.reply_text(text)

# /topup 指令：電話儲值流程
async def topup_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    lang = user_data.get('lang', 'EN')
    await update.message.reply_text(get_text("topup_ask_phone", lang))
    return TOPUP_PHONE

async def topup_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    lang = user_data.get('lang', 'EN')
    phone = update.message.text
    user_data['topup_phone'] = phone
    keyboard = [
        [InlineKeyboardButton("10", callback_data='topup_10'),
         InlineKeyboardButton("20", callback_data='topup_20'),
         InlineKeyboardButton("50", callback_data='topup_50')]
    ]
    await update.message.reply_text(
        get_text("topup_select_amount", lang),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return TOPUP_AMOUNT

async def topup_amount_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data  # 例如 "topup_20"
    amount = float(data.split('_')[1])
    user_data = context.user_data
    lang = user_data.get('lang', 'EN')
    phone = user_data.get('topup_phone', '')
    balance = user_data.get('balance', 0.0)
    if amount > balance:
        await query.edit_message_text(get_text("insufficient_balance", lang))
    else:
        user_data['balance'] = balance - amount
        text = get_text("topup_success", lang, phone=phone, amount=amount)
        await query.edit_message_text(text)
    return ConversationHandler.END

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN 未設定")
        return
    app = ApplicationBuilder().token(TOKEN).build()

    # 註冊指令與處理函式
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(lang_button, pattern="^lang_"))
    app.add_handler(CommandHandler("address", address))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("deposit", deposit))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(CommandHandler("vip", vip))
    app.add_handler(CommandHandler("card", card))

    # 閃兌會話 (選幣種 -> 輸入數量)
    exch_handler = ConversationHandler(
        entry_points=[CommandHandler("exchange", exchange)],
        states={
            EXCHANGE_COIN: [CallbackQueryHandler(exchange_coin_callback, pattern="^coin_")],
            EXCHANGE_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, exchange_amount)],
        },
        fallbacks=[]
    )
    app.add_handler(exch_handler)

    # 儲值會話 (輸入號碼 -> 選擇金額)
    topup_handler = ConversationHandler(
        entry_points=[CommandHandler("topup", topup_start)],
        states={
            TOPUP_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, topup_phone)],
            TOPUP_AMOUNT: [CallbackQueryHandler(topup_amount_callback, pattern="^topup_")],
        },
        fallbacks=[]
    )
    app.add_handler(topup_handler)

    print("Bot is running...")
    app.run_polling()
    print("Bot stopped.")

if __name__ == '__main__':
    main()