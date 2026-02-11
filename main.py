# test.py
import sys
import json
from io import BytesIO
from pprint import pprint

# Import services
from services.config import *
from services.auth import auth
from services.sharepoint_services import SharePointService
from services.preprocessing import process_file_to_dataframe, extract_columns_metadata

def print_separator(title=""):
    """Print fancy separator"""
    print("\n" + "="*70)
    if title:
        print(f"  {title}")
        print("="*70)
    else:
        print("="*70)

def test_read_data():
    """
    Test reading data from SharePoint and extracting column metadata
    Simulates what happens when user clicks 'Next' in Page 1
    """
    
    print_separator("🧪 TESTING: SharePoint Data Read + Column Extraction")
    
    # ========================================
    # 1. SETUP - Load Configuration
    # ========================================
    print("\n[1/6] 📋 Loading configuration...")
    try:
        # config = load_config()
        print(f"  ✓ Site ID: {SITE_ID[:20]}...")
        print(f"  ✓ Drive ID: {DRIVE_ID[:20]}...")
    except Exception as e:
        print(f"  ✗ Failed to load config: {e}")
        sys.exit(1)
    
    # ========================================
    # 2. USER INPUT SIMULATION (from Page 1)
    # ========================================
    print("\n[2/6] 📥 User Input (simulated):")
    
    # GANTI INI SESUAI FILE KAMU
    user_input = {
        'FolderPath': 'Fabric_Excel_Files/Test_Excel/Self_service_framework',           # Folder path di SharePoint
        'FilePattern': 'Online Retail.xlsx',           # Regex pattern untuk file
        'SheetName': 'Online Retail',                      # Kosongkan untuk sheet pertama
        'header': 0,                           # Row index untuk header
        'NeedBackup' : 'N',
        'FlexibleSchema' : "N",
        'CSVDelimiter' : None,
        'BackupFolderPath' : None,
        'CSVDelimiter': 'comma'
    }
    
    print(f"  • Folder Path    : {user_input['FolderPath']}")
    print(f"  • File Pattern   : {user_input['FilePattern']}")
    print(f"  • Sheet Name     : {user_input['SheetName'] or '(First sheet)'}")
    print(f"  • Header Row     : {user_input['header']}")
    print(f"  • CSV Delimiter  : {user_input['CSVDelimiter']}")
    print(f"  • Need Backup    : {user_input['NeedBackup']}")
    
    # ========================================
    # 3. INITIALIZE SHAREPOINT SERVICE
    # ========================================
    print("\n[3/6] 🔐 Initializing SharePoint Service...")
    try:
        sp_service = SharePointService(
            site_id=SITE_ID,
            drive_id=DRIVE_ID
        )
        print("  ✓ SharePoint service initialized")
        print(f"  ✓ Token acquired: {sp_service.token[:30]}...")
    except Exception as e:
        print(f"  ✗ Failed to initialize: {e}")
        sys.exit(1)
    
    # ========================================
    # 4. GET FILE METADATA
    # ========================================
    print("\n[4/6] 🔍 Fetching file metadata from SharePoint...")
    try:
        file_meta = sp_service.get_file_metadata(FolderPath=user_input['FolderPath'],FilePattern=user_input['FilePattern'])
        
        print(f"  ✓ File found: {file_meta['name']}")
        print(f"  • File ID       : {file_meta['file_id'][:30]}...")
        # print(f"  • File Size     : {file_meta['file_size']:,} bytes")
        print(f"  • Folder Name   : {file_meta.get('folder_name', 'Root')}")
        
        # Optional: Create backup
        if user_input['NeedBackup'] == 'Y':
            print("\n  💾 Creating backup...")
            backup_result = sp_service.create_backup(
                file_id=file_meta['file_id'],
                file_name=file_meta['name'],
                parent_folder_id=file_meta['parent_folder_id'],
                backup_FolderPath='Data/Backup'
            )
            print(f"  ✓ Backup created: {backup_result['backup_name']}")
        
    except Exception as e:
        print(f"  ✗ Failed to get file metadata: {e}")
        sys.exit(1)
    
    # ========================================
    # 5. DOWNLOAD & PROCESS FILE
    # ========================================
    print("\n[5/6] 📊 Downloading and processing file...")
    try:
        # Download file content
        print("  • Downloading file...")
        file_bytes = sp_service.download_file(file_meta['download_url'])
        print(f"  ✓ Downloaded {len(file_bytes.getvalue()):,} bytes")
        
        # Process to DataFrame
        print("  • Converting to DataFrame...")
        df = process_file_to_dataframe(
            file_bytes=file_bytes,
            file_name=file_meta['name'],
            sheet_name=user_input['SheetName'] if user_input['SheetName'] else None,
            header=user_input['header'],
            csv_delimiter=user_input['CSVDelimiter']
        )
        
        print(f"  ✓ DataFrame created: {len(df):,} rows × {len(df.columns)} columns")
        
    except Exception as e:
        print(f"  ✗ Failed to process file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # ========================================
    # 6. EXTRACT COLUMN METADATA
    # ========================================
    print("\n[6/6] 🔬 Extracting column metadata...")
    try:
        columns_info = extract_columns_metadata(df)
        print(f"  ✓ Extracted metadata for {len(columns_info)} columns")
    except Exception as e:
        print(f"  ✗ Failed to extract column metadata: {e}")
        sys.exit(1)
    
    # ========================================
    # RESULTS - What will be sent to Page 2
    # ========================================
    print_separator("📦 DATA THAT WILL BE SENT TO PAGE 2")
    
    print("\n📋 COLUMNS INFO (for Page 2 configuration):")
    print("-" * 70)
    
    for col_name, col_info in columns_info.items():
        print(f"\n🔹 Column: {col_name}")
        print(f"   • Data Type (pandas)  : {col_info['dtype']}")
        print(f"   • Inferred Type       : {col_info['inferred_type']}")
        print(f"   • Null Count          : {col_info['null_count']} ({col_info['null_percentage']}%)")
        print(f"   • Unique Values       : {col_info['unique_count']}")
        print(f"   • Sample Values       : {col_info['sample_values']}")
    
    print("\n" + "-" * 70)
    print(f"📊 Total Columns: {len(columns_info)}")
    print("-" * 70)
    
    # ========================================
    # DATA PREVIEW
    # ========================================
    print_separator("👁️  DATA PREVIEW (First 10 rows)")
    print(df.head(10).to_string())
    
    # ========================================
    # SESSION STATE SIMULATION
    # ========================================
    print_separator("💾 SESSION STATE (What Streamlit will store)")
    
    session_data = {
        'raw_df_shape': df.shape,
        'raw_df_sample': df.head(3).to_dict(),  # Only store sample
        'columns_info': columns_info,
        'file_metadata': {
            'name': file_meta['name'],
            'file_id': file_meta['file_id'],
            # 'file_size': file_meta['file_size'],
            'folder_name': file_meta.get('folder_name'),
            'total_rows': len(df),
            'is_sampled': len(df) > 1000  # Flag if we only stored sample
        },
        'input_params': user_input
    }
    
    print("\nSession State Structure:")
    pprint(session_data, depth=3, width=100)
    
    # ========================================
    # SAVE TO JSON (Optional)
    # ========================================
    print_separator("💾 SAVING TEST RESULTS")
    
    output_file = 'test_output.json'
    
    # Convert DataFrame sample to JSON-serializable format
    json_output = {
        'file_metadata': session_data['file_metadata'],
        'input_params': session_data['input_params'],
        'columns_info': session_data['columns_info'],
        'data_preview': df.head(10).to_dict(orient='records')
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✓ Test results saved to: {output_file}")
    
    # ========================================
    # SUMMARY
    # ========================================
    print_separator("✅ TEST SUMMARY")
    
    print(f"""
    File Processing: SUCCESS
    ────────────────────────────────────────
    • File Name      : {file_meta['name']}
    • Total Rows     : {len(df):,}
    • Total Columns  : {len(df.columns)}
    • Null Columns   : {sum(1 for c in columns_info.values() if c['null_count'] > 0)}
    
    Column Types Detected:
    """)
    
    # Count by inferred type
    type_counts = {}
    for col_info in columns_info.values():
        t = col_info['inferred_type']
        type_counts[t] = type_counts.get(t, 0) + 1
    
    for dtype, count in type_counts.items():
        print(f"    • {dtype.capitalize():<10} : {count} columns")
    
    print("\n" + "="*70)
    print("🎉 Testing completed successfully!")
    print("="*70 + "\n")
    
    return df, columns_info, file_meta


if __name__ == "__main__":
    try:
        df, columns_info, file_meta = test_read_data()
        
        # Interactive mode (optional)
        print("\n💡 TIP: You can now inspect the data in Python shell")
        print("   Variables available: df, columns_info, file_meta")
        print("\n   Example commands:")
        print("   >>> df.head()")
        print("   >>> df.info()")
        print("   >>> list(columns_info.keys())")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)