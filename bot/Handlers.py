import sys
from random import randint
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from bot.controllers.StorageController import get_storage_controller
from bot.controllers.MessagesController import MessagesController
from bot.controllers.NodesController import NodesController
from bot.modules.SetInterval import SetInterval


class Handlers:
    def __init__(self, settings, helpers):
        self.interval = None
        self.helpers = helpers
        self.settings = settings
        self.storage = get_storage_controller(settings, helpers)
        self.spreadsheet = self.storage  # Backwards compatibility
        self.nodes = NodesController(settings, self.storage, helpers)
        self.messages = MessagesController(helpers)

        self.seconds = 5
        if settings.NODE_DEBUG == 0:
            self.seconds = randint(30, (50 * settings.NODE_ID)) * settings.NODE_ID

    async def startup(self, application) -> None:
        await application.bot.send_message(
            chat_id=self.settings.TELEGRAM_MAIN_GROUP,
            text=f"I'm back up and running! 🚀\nNext check in {self.seconds} seconds ⏱️",
            parse_mode=ParseMode.HTML
        )

        self.interval = SetInterval(self.helpers, self.seconds, self.nodes.handle, application)

    async def reboot_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await self.messages.send_message(context, update, f"I'm going to reboot 🌀", True)
        self.interval.cancel()
        sys.exit(0)

    async def disable_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if hasattr(self.storage, 'update_node_check'):
            self.storage.update_node_check(self.settings.NODE_ID, 'FALSE')
        else:
            row = self.settings.NODE_ID + 1
            self.spreadsheet.update_main_data(row, 11, 'FALSE')

    async def enable_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if hasattr(self.storage, 'update_node_check'):
            self.storage.update_node_check(self.settings.NODE_ID, 'TRUE')
        else:
            row = self.settings.NODE_ID + 1
            self.spreadsheet.update_main_data(row, 11, 'TRUE')

    async def disable_nodes_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        nodes = context.args or []

        for node in nodes:
            if hasattr(self.storage, 'update_node_check'):
                self.storage.update_node_check(int(node), 'FALSE')
            else:
                row = int(node) + 1
                self.spreadsheet.update_main_data(row, 11, 'FALSE')

    async def enable_nodes_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        nodes = context.args or []

        for node in nodes:
            if hasattr(self.storage, 'update_node_check'):
                self.storage.update_node_check(int(node), 'TRUE')
            else:
                row = int(node) + 1
                self.spreadsheet.update_main_data(row, 11, 'TRUE')

    async def check_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        battery_status, battery = self.helpers.get_battery_status()
        await self.messages.send_message(
            context,
            update,
            f"I am fully up! 🚀\nBattery Status: \n{battery_status}",
            True
        )
