import os
import time

from telegram.ext import Application, CommandHandler
from bot.Handlers import Handlers
from config.Settings import Settings
from bot.modules.Helpers import Helpers

settings = Settings()
helpers = Helpers(settings)

packet_loss = os.system(f"ping -c 1 8.8.8.8 > /dev/null 2>&1")
while packet_loss > 0:
    helpers.write_log('error', f"Internet connection not available!")
    time.sleep(30)
    packet_loss = os.system(f"ping -c 1 8.8.8.8 > /dev/null 2>&1")

handlers = Handlers(settings, helpers)


def main() -> None:
    application = Application.builder().token(settings.TELEGRAM_TOKEN).post_init(handlers.startup).build()
    application.add_handler(CommandHandler("reboot", handlers.reboot_command))
    application.add_handler(CommandHandler("enable", handlers.enable_command))
    application.add_handler(CommandHandler("disable", handlers.disable_command))
    application.add_handler(CommandHandler("enable_nodes", handlers.enable_nodes_command))
    application.add_handler(CommandHandler("disable_nodes", handlers.disable_nodes_command))
    application.add_handler(CommandHandler("check", handlers.check_command))
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
