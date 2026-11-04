import os
try:
    import gspread
    import pandas as pd
    from oauth2client.service_account import ServiceAccountCredentials
except ImportError:
    gspread = None
    pd = None
    ServiceAccountCredentials = None


class SpreadSheetController:
    def __init__(self, settings):
        if gspread is None or ServiceAccountCredentials is None:
            raise ImportError(
                "gspread, pandas, and oauth2client are required for SpreadSheetController. "
                "Install them or configure BACKEND_URL to use the serverless backend."
            )
        if not os.path.exists("google_credentials.json"):
            raise FileNotFoundError(
                "google_credentials.json was not found. "
                "Provide Google credentials or configure BACKEND_URL to use the serverless backend."
            )

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

    def get_nodes(self):
        return self.read_main_data()

    def save_node_heartbeat(self, node_id, timestamp, wan_ip, battery_status):
        node_data = pd.DataFrame({"TS": [timestamp], "WAN_IP": [wan_ip], "BATTERY_STATUS": [battery_status]})
        self.write_node_data(node_data)

    def update_node_ping(self, node_id, ping_ts, ping_result, node_name, node_status):
        row = int(node_id) + 1
        self.update_main_data(row, 6, ping_ts)
        self.update_main_data(row, 7, ping_result)
        self.update_main_data(row, 8, node_name)
        self.update_main_data(row, 9, node_status)

    def update_node_check(self, node_id, check):
        row = int(node_id) + 1
        val = 'TRUE' if str(check).upper() in ('TRUE', '1') else 'FALSE'
        self.update_main_data(row, 11, val)
