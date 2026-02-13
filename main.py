import os
import json
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.getenv('WIP_ID')
SHEET_NAME = 'ExcelConfig'

# ---- Auth dari .env ----
def get_credentials():
    token_data = json.loads(os.getenv('GOOGLE_TOKEN'))
    creds = Credentials(
        token=token_data['token'],
        refresh_token=token_data['refresh_token'],
        token_uri=token_data['token_uri'],
        client_id=token_data['client_id'],
        client_secret=token_data['client_secret'],
        scopes=token_data['scopes']
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds

print("✅ Auth berhasil!")

# ---- Data ----
new_row = [
    268,                                                        # ExcelConfigId
    402,                                                        # FwkTriggerId
    "dbo",                                                      # SchemaName
    "Online Retail.xlsx",                                       # FileName
    "Online Retail.xlsx",                                       # FilePattern
    "google.com",                                               # URL
    "Fabric_Excel_Files/Test_Excel/Self_service_framework",     # FolderPath
    "Excel_Online_Retail",                                      # TableName
    "Online Retail",                                            # SheetName
    "NULL",                                                     # DataflowId
    "NULL",                                                     # DataflowWorkspaceId
    "NULL",                                                     # KeyColumnsList
    "NULL",                                                     # ColumnsExcludeMap
    "NULL",                                                     # ColumnType
    8,                                                          # Actions
    8,                                                          # Actions
    1,                                                          # HeaderRowsToDelete
    "NULL",                                                     # FwkTargetId
    "Full-Load",                                                # IngestionMode
    "N",                                                        # NeedBackup
    "NULL",                                                     # BackupFolderPath
    "N",                                                        # FlexibleSchema
    "N",                                                        # IsStaging
    "Y",                                                        # IsActive
    "N",                                                        # ExpectedEmpty
    "NULL",                                                     # CSVDelimiter
    "2/9/2026 11:04:03",                                        # LastModifiedDate
    "Naufal",                                                   # LastModifiedBy
    "Jokowi",                                                   # DataOwner
]

# ---- Append ----
def append_row(data: list):
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    body = {'values': [data]}

    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f'{SHEET_NAME}!A1',
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    print(f"✅ Berhasil append! Range: {result['updates']['updatedRange']}")

append_row(new_row)