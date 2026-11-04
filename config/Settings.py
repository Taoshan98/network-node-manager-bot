from decouple import config


class Settings:
    def __init__(self):
        self.TELEGRAM_TOKEN = config('TELEGRAM_TOKEN', default='')
        self.TELEGRAM_MAIN_GROUP = config('TELEGRAM_MAIN_GROUP', default='')
        self.NODE_ID = int(config('NODE_ID', default=1))
        self.NODE_HAS_BATTERY = int(config('NODE_HAS_BATTERY', default=0))
        self.NODE_TYPE = config('NODE_TYPE', default='LINUX')
        self.NODE_DEBUG = int(config('NODE_DEBUG', default=0))

        # Backend serverless settings
        self.BACKEND_URL = config('BACKEND_URL', default=None)
        self.BACKEND_API_KEY = config('BACKEND_API_KEY', default=None)

        # Google Spreadsheet settings (optional)
        self.SPREADSHEET_URL = config('SPREADSHEET_URL', default=None)
        self.MAIN_SHEET_ID = config('MAIN_SHEET_ID', default=None)
        self.NODE_SHEET_ID = config('NODE_SHEET_ID', default=None)

        # Storage backend mode: BACKEND, SPREADSHEET, or COMBINED
        configured_backend = config('DATA_BACKEND', default=None)
        if configured_backend:
            self.DATA_BACKEND = configured_backend.upper()
        elif self.BACKEND_URL and self.SPREADSHEET_URL:
            self.DATA_BACKEND = 'COMBINED'
        elif self.BACKEND_URL:
            self.DATA_BACKEND = 'BACKEND'
        elif self.SPREADSHEET_URL:
            self.DATA_BACKEND = 'SPREADSHEET'
        else:
            self.DATA_BACKEND = 'BACKEND'
