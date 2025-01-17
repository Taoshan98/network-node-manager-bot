from decouple import config


class Settings:
    def __init__(self):
        self.TELEGRAM_TOKEN = config('TELEGRAM_TOKEN')
        self.TELEGRAM_MAIN_GROUP = config('TELEGRAM_MAIN_GROUP')
        self.NODE_ID = int(config('NODE_ID'))
        self.NODE_HAS_BATTERY = int(config('NODE_HAS_BATTERY'))
        self.SPREADSHEET_URL = config('SPREADSHEET_URL')
        self.MAIN_SHEET_ID = config('MAIN_SHEET_ID')
        self.NODE_SHEET_ID = config('NODE_SHEET_ID')
        self.NODE_TYPE = config('NODE_TYPE')
        self.NODE_DEBUG = int(config('NODE_DEBUG'))
