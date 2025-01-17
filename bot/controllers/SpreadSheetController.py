import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials


class SpreadSheetController:
    def __init__(self, settings):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", scope)
        client = gspread.authorize(credentials)

        self.node_sheet = client.open_by_url(settings.SPREADSHEET_URL).get_worksheet_by_id(settings.NODE_SHEET_ID)
        self.main_sheet = client.open_by_url(settings.SPREADSHEET_URL).get_worksheet_by_id(settings.MAIN_SHEET_ID)

    def read_node_data(self):
        # Leggi i dati esistenti dal foglio come DataFrame

        records = self.node_sheet.get_all_records()
        df = pd.DataFrame(records)
        return df

    def write_node_data(self, data):
        """
        Scrive nuovi dati nello spreadsheet
        :param data: DataFrame contenente i dati da aggiungere
        """

        rows_to_add = data.values.tolist()
        self.node_sheet.append_rows(rows_to_add)

    def read_main_data(self):
        # Leggi i dati esistenti dal foglio come DataFrame

        records = self.main_sheet.get_all_records()
        df = pd.DataFrame(records)
        return records

    def update_main_data(self, row, cell, value):
        # Leggi i dati esistenti dal foglio come DataFrame

        self.main_sheet.update_cell(row, cell, value)
