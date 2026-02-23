from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from util import header


GPT_CHAT = 1


def get_gpt_conversation_handler(gpt_service):

    async def start_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await header(update, context)
        # await update.message.reply_text(
        #     "🤖 GPT режим активовано.\n" "Пишіть питання.\n" "Для виходу — /stop"
        # )
        return GPT_CHAT

    async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_text = update.message.text

        await update.message.reply_text("⏳ Думаю...")

        try:
            answer = await gpt_service.ask(user_id, user_text)
            await update.message.reply_text(answer)
        # except Exception:
        #     await update.message.reply_text("Сталася помилка. Спробуйте пізніше.")
        except Exception as e:
            await update.effective_message.reply_text(
                f"Сталася помилка{e}. Спробуйте пізніше"
            )

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


