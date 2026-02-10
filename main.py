import pandas as pd
from io import BytesIO
from services.config import SITE_ID, DRIVE_ID
from services.auth import auth
from services.preprocessing import read_data

FilePattern = "Online Retail.xlsx"
FolderPath = "Fabric_Excel_Files/Test_Excel/Self_service_framework"
SheetName = "Online Retail"
Header = "1"
NeedBackup = "N"
FlexibleSchema = "N"
CSVDelimiter = None
BackupFolderPath = None

TOKEN = auth.get_graph_token()
Header = int(Header)
Header -= 1
FolderURL = f"https://graph.microsoft.com/v1.0/sites/{SITE_ID}/drives/{DRIVE_ID}/root:/{FolderPath}:/children"

try:
    print("="*60)
    print("test read data")
    print("="*60)
    df, DynamicTableName = read_data(FolderPath, FilePattern, SheetName, Header, TOKEN, SITE_ID, DRIVE_ID, CSVDelimiter, NeedBackup, BackupFolderPath)

    if df is not None:
        print("="*60)
        print("SUCCESS")
        print("="*60)
        print(f"Table Name: {DynamicTableName}")
        print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"\nFirst 5 rows:")
        print(df.head())
        print(f"\nData types:")
        print(df.dtypes)
        print(f"\nColumn names:")
        print(df.columns.tolist())
    else:
        print("\n❌ FAILED: No data returned")

except Exception as e:
    print("\n" + "="*60)
    print("❌ ERROR")
    print("="*60)
    print(f"Error: {type(e).__name__}")
    print(f"Message: {str(e)}")
    import traceback
    print("\nFull traceback:")