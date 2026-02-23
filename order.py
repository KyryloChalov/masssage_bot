# order.py

import re
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from util import header, extract_phone

# ---- STATES ----
ASK_PHONE, ASK_TIME, CONFIRM = range(3)


# -----------------------------
# 🚀 ENTRY POINT
# -----------------------------
async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["order"] = {}

    await header(update, context)

    await update.effective_message.reply_text(
        "Будь ласка, вкажіть ваш номер телефону 📞"
    )

    return ASK_PHONE


# -----------------------------
# 📞 ASK PHONE
# -----------------------------
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone_raw = update.message.text.strip()
    phone = extract_phone(phone_raw)

    if not phone:
        await update.message.reply_text("Невірний формат телефону. Спробуйте ще раз.")
        return ASK_PHONE

    context.user_data["order"]["phone"] = phone

    await update.message.reply_text("На який час бажаєте записатися? ⏰")
    return ASK_TIME


# -----------------------------
# ⏰ ASK TIME
# -----------------------------
async def ask_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time_text = update.message.text.strip()
    context.user_data["order"]["time"] = time_text

    phone = context.user_data["order"]["phone"]

    await update.message.reply_text(
        f"Підтвердьте запис:\n\n"
        f"📞 Телефон: {phone}\n"
        f"⏰ Час: {time_text}\n\n"
        f"Напишіть 'так' для підтвердження або 'ні' для скасування."
    )

    return CONFIRM


# -----------------------------
# ✅ CONFIRM
# -----------------------------
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()

    if text not in ["так", "ні"]:
        await update.message.reply_text("Будь ласка, напишіть 'так' або 'ні'.")
        return CONFIRM

    if text == "ні":
        await update.message.reply_text("Замовлення скасовано.")
        context.user_data.clear()
        return ConversationHandler.END

    # ---- ВІДПРАВКА АДМІНУ ----
    order = context.user_data["order"]

    admin_chat_id = context.bot_data.get("ADMIN_ID")

    if admin_chat_id:
        await context.bot.send_message(
            chat_id=admin_chat_id,
            text=(
                "🆕 НОВЕ ЗАМОВЛЕННЯ\n\n"
                f"📞 Телефон: {order['phone']}\n"
                f"⏰ Час: {order['time']}"
            ),
        )

    await update.message.reply_text(
        "Дякуємо! Заявку прийнято. Менеджер зв'яжеться з вами найближчим часом."
    )

    context.user_data.clear()
    return ConversationHandler.END


# -----------------------------
# ❌ CANCEL
# -----------------------------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Замовлення скасовано.")
    return ConversationHandler.END


# -----------------------------
# 🧩 HANDLER BUILDER
# -----------------------------
def get_order_conversation_handler():
    # print('get_order_conversation_handler started')
    return ConversationHandler(
        entry_points=[CommandHandler("order", start_order)],
        states={
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_time)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="order_conversation",
        persistent=False,
    )
