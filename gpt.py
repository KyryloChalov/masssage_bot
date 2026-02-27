from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from include.from_env import TELEGRAM_KYRYLO_ID
from include.util import extract_phone
from include.util_telegram import header

from include.colors import RED, RESET


GPT_CHAT = 1


def get_gpt_conversation_handler(gpt_service):

    async def start_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await header(update, context)
        return GPT_CHAT

    async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_text = update.message.text.strip()

        my_message = await update.message.reply_text("⏳ . . . ")

        # ---------- GPT RESPONSE ----------
        try:
            answer = await gpt_service.ask(user_id, user_text)

            await my_message.edit_text(answer)

            # отримано номер телефону?
            phone = extract_phone(user_text)

            if phone:
                print("chat >>> phone: ", phone)
                user = update.effective_user

                await header(update, context, "thanks")

                gpt_history = await gpt_service.history_from_db(user.id)
                dialog = await parse_dialog_for_output(gpt_history)

                order_data = {
                    "name": user.full_name,
                    "username": user.username,
                    "user_id": user.id,
                    "phone": phone,
                    "dialog": dialog,
                }

                await notify_admin(context, order_data)

        except Exception as e:
            await update.effective_message.reply_text(
                "Сталася помилка. Спробуйте пізніше"
            )
            print(RED, f"Сталася помилка: {e}. Спробуйте пізніше", RESET)
        return GPT_CHAT

    async def parse_dialog_for_output(dialog: list):
        output = ""
        for entry in dialog:
            role = entry["role"]
            content = entry["content"]
            output += f"{role.upper()}: {content}\n\n"
        return output

    async def stop_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
        gpt_service.repo.clear_history(update.effective_user.id)
        await header(update, context)
        return ConversationHandler.END

    return ConversationHandler(
        entry_points=[CommandHandler("gpt", start_gpt)],
        states={GPT_CHAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, chat)]},
        fallbacks=[CommandHandler("stop", stop_gpt)],
        per_user=True,
        per_chat=True,
    )


async def notify_admin(context, order_data):
    message = f"""
🚀 СТАТУС: GPT режим
🆕 НОВЕ GPT-ЗАМОВЛЕННЯ

👤 Ім'я:     {order_data.get("name")}
📎 Username: @{order_data.get("username")}
🆔 ID:       {order_data.get("user_id")}
📞 Телефон:  {order_data.get("phone")}

💬 Останній діалог:\n{order_data.get("dialog")}
"""
    await context.bot.send_message(chat_id=TELEGRAM_KYRYLO_ID, text=message)

    # кілька адміністраторів - на майбутнє
    # for admin_id in ADMIN_CHAT_IDS:
    #     await context.bot.send_message(
    #         chat_id=admin_id,
    #         text=message
    #     )
