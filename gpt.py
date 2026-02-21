# gpt.py

from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

GPT_CHAT = 1


def get_gpt_conversation_handler(gpt_service):

    async def start_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["gpt_history"] = []

        await update.effective_message.reply_text(
            "🤖 GPT режим активовано.\n"
            "Напишіть питання.\n"
            "Для виходу — /stop"
        )

        return GPT_CHAT


    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.effective_message.text

        await update.effective_message.reply_text("⏳ Думаю...")

        try:
            answer = await gpt_service.send_question(
                system_prompt="Ти помічник масажного салону.",
                user_input=user_text,
                max_output_tokens=400,
            )

            await update.effective_message.reply_text(answer)

        except Exception:
            await update.effective_message.reply_text(
                "Сталася помилка. Спробуйте пізніше."
            )

        return GPT_CHAT


    async def stop_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data.pop("gpt_history", None)

        await update.effective_message.reply_text("GPT режим завершено.")

        return ConversationHandler.END


    return ConversationHandler(
        entry_points=[CommandHandler("gpt", start_gpt)],
        states={
            GPT_CHAT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
            ],
        },
        fallbacks=[
            CommandHandler("stop", stop_gpt),
        ],
        per_user=True,
        per_chat=True,
    )
