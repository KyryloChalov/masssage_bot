from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import RateLimitError
# import json
# import time

from include.from_env import TELEGRAM_KYRYLO_ID
# from include.sys_prompt import BUSINESS_INFO, SYSTEM_PROMPT
from include.util import header, extract_phone

# from storage.gpt_repository import get_history

CONFIRM_MESSAGE = "Дякую! Передаю інформацію менеджеру.\n\n>>> Очікуйте на дзвінок 📞"
# last_orders: dict[str, str] = {}

GPT_CHAT = 1


# # чат повертає відповідь у форматі json
# # {"order": false, "message": "твоя відповідь клієнту"}
# # функція normalize_answer виводить на екран тільки message
# def normalize_answer(answer_raw):
#     if isinstance(answer_raw, dict):
#         return answer_raw.get("message")
#     elif isinstance(answer_raw, str):
#         try:
#             data = json.loads(answer_raw)
#             return data.get("message")
#         except json.JSONDecodeError:
#             return answer_raw  # рядок не JSON, просто друкуємо


def get_gpt_conversation_handler(gpt_service):

    async def start_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await header(update, context)
        return GPT_CHAT

    async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_text = update.message.text.strip()


        #     input_text = f"""
        # ІНФОРМАЦІЯ ПРО СЕРВІС:{BUSINESS_INFO}
        # ІСТОРІЯ ПИТАНЬ КЛІЄНТА:{user_history}
        # ПИТАННЯ КЛІЄНТА:{user_text}
        # """
        try:
            my_message = await update.message.reply_text("⏳ . . . ")
            # завдання - отримати номер телефону юзера
            phone = extract_phone(user_text)

            if phone:
                print("chat >>> phone: ", phone)

                # gpt_history = get_history

                # order_data = {
                #     "name": user.full_name,
                #     "username": user.username,
                #     "user_id": user.id,
                #     "phone": phone,
                #     # "dialog": gpt_history,
                # }

                # await notify_admin(context, order_data)

                # header?
                await my_message.edit_text(CONFIRM_MESSAGE)
                await header(update, context, "thanks")

                return

            # якщо це не замовлення → працюємо через GPT
            # ---------- GPT RESPONSE ----------
            try:
                answer = await gpt_service.ask(user_id, user_text)
                # await update.message.reply_text(answer)

                await my_message.edit_text(answer)

            except Exception as e:
                await update.effective_message.reply_text(
                    f"Сталася помилка{e}. Спробуйте пізніше"
                )
                print("user_id: ", user_id)
                print("user_text: ", user_text)
                print("answer: ", answer)

        except RateLimitError:
            await update.message.reply_text(
                update,
                context,
                "Зараз надто багато запитів. Спробуйте через кілька секунд.",
            )
        except Exception as e:
            await update.message.reply_text(update, context, f"Виникла помилка: {e}")

        return GPT_CHAT

    async def stop_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
        gpt_service.repo.clear_history(update.effective_user.id)
        await header(update, context)
        # await update.message.reply_text("GPT режим завершено.")
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

👤 Ім'я: {order_data.get("name")}
📎 Username: @{order_data.get("username")}
🆔 ID: {order_data.get("user_id")}
📞 Телефон: {order_data.get("phone")}

💬 Останній діалог:
{order_data.get("dialog")}
"""
    await context.bot.send_message(chat_id=TELEGRAM_KYRYLO_ID, text=message)

    # кілька адміністраторів - на майбутнє
    # for admin_id in ADMIN_CHAT_IDS:
    #     await context.bot.send_message(
    #         chat_id=admin_id,
    #         text=message
    #     )


# def save_order_to_file(order_data):
#     order_data["created_at"] = datetime.now().isoformat()

#     with open("orders_log.json", "a", encoding="utf-8") as f:
#         f.write(json.dumps(order_data, ensure_ascii=False) + "\n")
