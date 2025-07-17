import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# 模擬用戶資料庫（可換成真實資料庫）
user_data = {}

# 讀取 BOT_TOKEN
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 主選單按鈕
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("💰 餘額查詢", callback_data="check_balance")],
        [InlineKeyboardButton("🎁 發紅包", callback_data="send_redpacket")],
        [InlineKeyboardButton("💸 提領", callback_data="withdraw")],
        [InlineKeyboardButton("👑 VIP 升級", callback_data="vip")],
        [InlineKeyboardButton("📞 客服支持", url="https://t.me/LYVOXIS")],
    ]
    return InlineKeyboardMarkup(keyboard)

# /start 指令
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {"balance": 100.0, "vip": False}
    await update.message.reply_text(
        "歡迎使用 LYVOXIS 錢包機器人 👑\n請選擇以下功能：",
        reply_markup=get_main_menu()
    )

# 處理按鈕事件
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id not in user_data:
        user_data[user_id] = {"balance": 0.0, "vip": False}

    if query.data == "check_balance":
        balance = user_data[user_id]["balance"]
        vip = "是" if user_data[user_id]["vip"] else "否"
        await query.edit_message_text(f"💼 您目前的餘額：{balance:.2f} U\n👑 VIP 身分：{vip}",
                                      reply_markup=get_main_menu())

    elif query.data == "send_redpacket":
        user_data[user_id]["balance"] -= 5
        await query.edit_message_text("🎁 紅包已發送！已扣除 5 U。",
                                      reply_markup=get_main_menu())

    elif query.data == "withdraw":
        fee = 1.0 + user_data[user_id]["balance"] * 0.005
        user_data[user_id]["balance"] -= fee
        await query.edit_message_text(f"💸 已提領，手續費約 {fee:.2f} U 已扣除。",
                                      reply_markup=get_main_menu())

    elif query.data == "vip":
        user_data[user_id]["vip"] = True
        await query.edit_message_text("🎉 恭喜升級 VIP！您享有更低手續費與紅包返利。",
                                      reply_markup=get_main_menu())

# 建立機器人主應用程式
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.run_polling()