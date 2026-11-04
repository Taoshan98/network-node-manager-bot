from bot.controllers.BackendController import BackendController
from bot.controllers.SpreadSheetController import SpreadSheetController
from bot.controllers.CombinedStorageController import CombinedStorageController


def get_storage_controller(settings, helpers=None):
    """
    Factory function returning the configured storage controller.
    Supports 'BACKEND', 'SPREADSHEET', and 'COMBINED' modes.
    """
    backend_mode = getattr(settings, "DATA_BACKEND", "BACKEND").upper()

    if backend_mode == "COMBINED":
        return CombinedStorageController(settings, helpers)
    elif backend_mode == "SPREADSHEET":
        return SpreadSheetController(settings)
    else:
        return BackendController(settings, helpers)
