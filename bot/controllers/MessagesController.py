from telegram.constants import ParseMode


class MessagesController:
    def __init__(self, helpers):
        self.helpers = helpers
        self.except_message = (
            f"\n\nThere was a problem, check the logs."
        )

    async def send_message(self, context, update, message, send_to_chat=False):
        try:
            chat_id = update.message.from_user.id
            message_thread_id = None

            if send_to_chat:
                chat_id = update.message.chat_id
                message_thread_id = update.message.message_thread_id

            await context.bot.send_message(
                message_thread_id=message_thread_id,
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            chat_id = update.message.chat_id

            await context.bot.send_message(
                chat_id=chat_id,
                text=f"{message}{self.except_message}",
                parse_mode=ParseMode.HTML
            )

            self.helpers.write_log('error', f"{update}")
            self.helpers.write_log('error', f"{type(e).__name__} – {e}")

    async def send_photo(self, context, update, photo, message, send_to_chat=False):
        try:
            chat_id = update.message.from_user.id
            message_thread_id = None
            if send_to_chat:
                chat_id = update.message.chat_id
                message_thread_id = update.message.message_thread_id

            await context.bot.send_photo(
                message_thread_id=message_thread_id,
                chat_id=chat_id,
                photo=photo,
                caption=message,
                parse_mode=ParseMode.HTML
            )

        except Exception as e:
            await context.bot.send_photo(
                chat_id=update.message.chat_id,
                photo=photo,
                caption=f"{message}{self.except_message}",
                parse_mode=ParseMode.HTML
            )
            self.helpers.write_log('error', f"{update}")
            self.helpers.write_log('error', f"{type(e).__name__} – {e}")

    async def send_video(self, context, update, video, message, send_to_chat=False):
        try:
            chat_id = update.message.from_user.id
            message_thread_id = None
            if send_to_chat:
                chat_id = update.message.chat_id
                message_thread_id = update.message.message_thread_id

            self.helpers.write_log('error', f"{message}")

            await context.bot.send_video(
                message_thread_id=message_thread_id,
                chat_id=chat_id,
                video=video,
                caption=message,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            await context.bot.send_video(
                chat_id=update.message.chat_id,
                video=video,
                caption=f"{message}{self.except_message}",
                parse_mode=ParseMode.HTML
            )

            self.helpers.write_log('error', f"{update}")
            self.helpers.write_log('error', f"{type(e).__name__} – {e}")
