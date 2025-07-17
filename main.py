import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# 讀取 Telegram Bot Token（從 Render 或 Replit 的環境變數）
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# 用戶資料暫存（實際可改為資料庫）
user_data = {}

# /start 指令處理
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id

    # 建立用戶基本資料
    if uid not in user_data:
        user_data[uid] = {
            "balance": 0.0,
            "vip": False,
        }

    keyboard = [
        [InlineKeyboardButton("💰 查詢餘額", callback_data="balance")],
        [InlineKeyboardButton("🪙 充值通知", callback_data="deposit")],
        [InlineKeyboardButton("📤 我要提幣", callback_data="withdraw")],
        [InlineKeyboardButton("👑 購買 VIP", callback_data="vip")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 歡迎使用 LYVOXIS 數位錢包機器人！\n請選擇功能 👇", reply_markup=reply_markup
    )

# 按鈕選單處理
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id

    if uid not in user_data:
        user_data[uid] = {"balance": 0.0, "vip": False}

    if query.data == "balance":
        balance = user_data[uid]["balance"]
        await query.edit_message_text(f"💼 您目前錢包餘額為：{balance:.2f} U")
    elif query.data == "deposit":
        await query.edit_message_text(
            "🪙 請將款項匯入以下錢包地址：\n`TXXX...`（僅支援 TRC20）\n系統將自動入金"
        )
    elif query.data == "withdraw":
        await query.edit_message_text(
            "📤 請點選下列連結填寫提幣表單：\nhttps://yourdomain.com/withdraw"
        )
    elif query.data == "vip":
        await query.edit_message_text(
            "👑 VIP 購買方案：\n\n"
            "🔹 3個月 - 14.9 USDT\n"
            "🔹 6個月 - 18.9 USDT\n"
            "🔹 12個月 - 32.9 USDT\n\n"
            "請轉帳至指定地址並聯絡客服開通"
        )

# 主程式
if __name__ == "__main__":
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN 環境變數未設定")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))

    print("🤖 機器人已啟動...")
    app.run_polling()