from telegram.ext import Application, CommandHandler
from bot.Handlers import Handlers
from config.Settings import Settings
from bot.modules.Helpers import Helpers


def main() -> None:
    settings = Settings()
    helpers = Helpers(settings)

    helpers.wait_for_internet()

    handlers = Handlers(settings, helpers)

    try:
        application = Application.builder().token(settings.TELEGRAM_TOKEN).post_init(handlers.startup).build()
        application.add_handler(CommandHandler("reboot", handlers.reboot_command))
        application.add_handler(CommandHandler("enable", handlers.enable_command))
        application.add_handler(CommandHandler("disable", handlers.disable_command))
        application.add_handler(CommandHandler("enable_nodes", handlers.enable_nodes_command))
        application.add_handler(CommandHandler("disable_nodes", handlers.disable_nodes_command))
        application.add_handler(CommandHandler("check", handlers.check_command))
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        helpers.write_log('error', f"Bot Crashed. {type(e).__name__} – {e}")


if __name__ == "__main__":
    main()
