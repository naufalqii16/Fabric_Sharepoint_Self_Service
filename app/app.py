# app/app.py
import sys
import os

# ============================================
# FIX PYTHON PATH
# ============================================
current_file = os.path.abspath(__file__)
app_dir = os.path.dirname(current_file)
root_dir = os.path.dirname(app_dir)

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# ============================================
# IMPORTS
# ============================================
import streamlit as st
from services.config import SITE_ID, DRIVE_ID, validate_config
from services.sharepoint_services import SharePointService
from services.preprocessing import process_file_to_dataframe, extract_columns_metadata

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Excel Ingestion Configurator",
    page_icon="📊",
    layout="wide"
)

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
if 'step' not in st.session_state:
    st.session_state.step = 1

if 'file_data' not in st.session_state:
    st.session_state.file_data = None

if 'columns_info' not in st.session_state:
    st.session_state.columns_info = None

if 'user_input' not in st.session_state:
    st.session_state.user_input = {}

if 'df_preview' not in st.session_state:
    st.session_state.df_preview = None

# ✅ TAMBAHAN: Flag untuk track apakah data sudah di-fetch
if 'data_fetched' not in st.session_state:
    st.session_state.data_fetched = False

# ✅ TAMBAHAN: Store form values dari Step 1
if 'form_values' not in st.session_state:
    st.session_state.form_values = {
        'sp_url': '',
        'folder_path': '',
        'file_name': '',
        'extension': '.xlsx',
        'delimiter': ',',
        'sheet_name': '',
        'header_row': 0,
        'need_backup': False
    }

# ============================================
# HELPER FUNCTIONS
# ============================================
def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

def reset_app():
    """Reset all session state"""
    st.session_state.step = 1
    st.session_state.file_data = None
    st.session_state.columns_info = None
    st.session_state.user_input = {}
    st.session_state.df_preview = None
    st.session_state.data_fetched = False  # ✅ TAMBAHAN
    st.session_state.form_values = {  # ✅ TAMBAHAN
        'sp_url': '',
        'folder_path': '',
        'file_name': '',
        'extension': '.xlsx',
        'delimiter': ',',
        'sheet_name': '',
        'header_row': 0,
        'need_backup': False
    }

# ✅ UBAH: Fungsi reset_page2_data (hanya reset page 2, form step 1 tetap)
def reset_page2_data():
    """Reset hanya data page 2 (column selections)"""
    st.session_state.file_data = None
    st.session_state.columns_info = None
    st.session_state.df_preview = None
    st.session_state.data_fetched = False
    # user_input key_columns akan direset saat fetch
    if 'key_columns' in st.session_state.user_input:
        del st.session_state.user_input['key_columns']

def process_user_input():
    """
    Backend processing: Read file from SharePoint and extract column metadata
    This runs when user clicks 'Fetch' on Step 1
    """
    with st.spinner("🔄 Processing your request..."):
        try:
            # Step 1: Get user input from session state
            user_input = st.session_state.user_input
            
            st.info("📂 Connecting to SharePoint...")
            
            # Step 2: Initialize SharePoint Service
            sp_service = SharePointService(
                site_id=SITE_ID,
                drive_id=DRIVE_ID
            )
            
            st.info(f"🔍 Searching for file: {user_input['file_name']}")
            
            # Step 3: Get file metadata
            file_meta = sp_service.get_file_metadata(
                FolderPath=user_input['folder_path'],
                FilePattern=user_input['file_name']
            )
            
            st.success(f"✅ File found: {file_meta['name']}")
            
            # Step 4: Download file
            st.info("⬇️ Downloading file...")
            file_bytes = sp_service.download_file(file_meta['download_url'])
            
            # Step 5: Process to DataFrame
            st.info("📊 Processing file...")
            
            # Determine CSV delimiter if applicable
            csv_delimiter = None
            if user_input['extension'] == '.csv':
                delimiter_map = {
                    ',': 'comma',
                    ';': 'semicolon',
                    '\t': 'tab',
                    '|': 'pipe'
                }
                csv_delimiter = delimiter_map.get(user_input.get('delimiter', ','), 'comma')
            
            df = process_file_to_dataframe(
                file_bytes=file_bytes,
                file_name=file_meta['name'],
                sheet_name=user_input.get('sheet_name') if user_input.get('sheet_name') else None,
                header=user_input.get('header_row', 0),
                csv_delimiter=csv_delimiter or 'comma'
            )
            
            st.success(f"✅ DataFrame created: {len(df):,} rows × {len(df.columns)} columns")
            
            # Step 6: Extract column metadata
            st.info("🔬 Extracting column information...")
            columns_info = extract_columns_metadata(df)
            
            # Step 7: Save to session state
            st.session_state.file_data = file_meta
            st.session_state.columns_info = columns_info
            st.session_state.df_preview = df.head(100)  # Store sample only
            st.session_state.data_fetched = True  # ✅ TAMBAHAN: Set flag to True
            
            st.success("✅ Processing complete!")
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            with st.expander("🔍 Show detailed error"):
                st.code(traceback.format_exc())
            return False

# ============================================
# HEADER
# ============================================
st.title("⚙️ Configuration Panel")
st.caption("Input the needed config here")

# Validate config on startup
try:
    validate_config()
except Exception as e:
    st.error(f"❌ Configuration Error: {e}")
    st.info("💡 Please check your .env file")
    st.stop()

# Progress bar
progress_mapping = {1: 0.33, 2: 0.66, 3: 1.0}
st.progress(progress_mapping.get(st.session_state.step, 0.33))

# ============================================
# STEP 1: SOURCE & FILE CONFIGURATION
# ============================================
if st.session_state.step == 1:
    st.subheader("📍 Step 1: Source & File")
    
    # ✅ UBAH: Tidak pakai st.form lagi, karena perlu 2 button terpisah
    st.text("Source Location")
    
    # ✅ TAMBAHAN: Use stored form values as default
    form_vals = st.session_state.form_values
    
    # SharePoint URL (optional for display)
    sp_url = st.text_input(
        "Sharepoint URL (optional)", 
        value=form_vals['sp_url'],  # ✅ TAMBAHAN: Default value
        placeholder="https://yourcompany.sharepoint.com/...",
        help="This is for reference only",
        key="input_sp_url"
    )
    
    # Folder Path (required)
    folder_path = st.text_input(
        "Folder Path*",
        value=form_vals['folder_path'],  # ✅ TAMBAHAN: Default value
        placeholder="e.g., Fabric_Excel_Files/Test_Excel",
        help="Path to the folder in SharePoint",
        key="input_folder_path"
    )
    
    # File details
    col1, col2 = st.columns(2)
    with col1:
        file_name = st.text_input(
            "File Name*",
            value=form_vals['file_name'],  # ✅ TAMBAHAN: Default value
            placeholder="e.g., Online Retail.xlsx",
            help="Exact filename including extension",
            key="input_file_name"
        )
    with col2:
        extension = st.selectbox(
            "Extension",
            [".xlsx", ".xls", ".csv"],
            index=[".xlsx", ".xls", ".csv"].index(form_vals['extension']),  # ✅ TAMBAHAN: Default
            help="File type",
            key="input_extension"
        )
    
    # CSV-specific options
    delimiter = None
    custom_delimiter = None
    if extension == ".csv":
        c1, c2 = st.columns(2)
        with c1:
            delimiter = st.selectbox(
                "Delimiter", 
                [",", ";", "\t", "|", "Custom"],
                key="input_delimiter"
            )
        with c2:
            if delimiter == "Custom":
                custom_delimiter = st.text_input(
                    "Input Custom Delimiter",
                    key="input_custom_delimiter"
                )
                if not custom_delimiter:
                    st.warning("⚠️ Custom delimiter cannot be empty!")
    
    # Additional file options
    col3, col4, col5 = st.columns(3)
    
    with col3:
        sheet_name = st.text_input(
            "Sheet Name",
            value=form_vals['sheet_name'],  # ✅ TAMBAHAN: Default value
            placeholder="Leave empty for first sheet",
            help="For Excel files only",
            key="input_sheet_name"
        )
    
    with col4:
        header_row = st.number_input(
            "Header Row Index",
            min_value=0,
            value=form_vals['header_row'],  # ✅ TAMBAHAN: Default value
            help="Row index where column headers are (0-indexed)",
            key="input_header_row"
        )
    
    with col5:
        st.markdown("<div style='padding-top: 32px;'></div>", unsafe_allow_html=True)
        need_backup = st.checkbox(
            "Create Backup",
            value=form_vals['need_backup'],  # ✅ TAMBAHAN: Default value
            help="Create backup copy before reading",
            key="input_need_backup"
        )
    
    st.divider()
    
    # ✅ UBAH: Validation
    mandatory_fields = [folder_path, file_name]
    all_filled = all(mandatory_fields)
    
    # ✅ UBAH: TWO SEPARATE BUTTONS
    col_fetch, col_next = st.columns([1, 1])
    
    with col_fetch:
        fetch_disabled = not all_filled
        if extension == ".csv" and delimiter == "Custom" and not custom_delimiter:
            fetch_disabled = True
        
        fetch_clicked = st.button(
            "📥 Fetch File Data",
            type="primary",
            disabled=fetch_disabled,
            width='stretch',
            key="btn_fetch"
        )
    
    with col_next:
        # ✅ TAMBAHAN: Next button hanya muncul kalau data sudah di-fetch
        next_disabled = not st.session_state.data_fetched
        next_clicked = st.button(
            "➡️ Next",
            type="secondary",
            disabled=next_disabled,
            width='stretch',
            key="btn_next_step1"
        )
    
    # ✅ UBAH: Handle Fetch button click
    if fetch_clicked:
        # ✅ TAMBAHAN: Save form values to session state
        st.session_state.form_values = {
            'sp_url': sp_url,
            'folder_path': folder_path,
            'file_name': file_name,
            'extension': extension,
            'delimiter': custom_delimiter if delimiter == "Custom" else delimiter,
            'sheet_name': sheet_name,
            'header_row': header_row,
            'need_backup': need_backup
        }
        
        # Save to user_input
        st.session_state.user_input = st.session_state.form_values.copy()
        
        # ✅ TAMBAHAN: Reset page 2 data when fetching new data
        reset_page2_data()
        
        # Process file and extract columns
        success = process_user_input()
        
        if success:
            st.success("✅ Data fetched successfully! Click 'Next' to continue.")
            st.rerun()
    
    # ✅ TAMBAHAN: Handle Next button click
    if next_clicked:
        next_step()
        st.rerun()
    
    # ✅ TAMBAHAN: Show status if data already fetched
    if st.session_state.data_fetched:
        st.success("✅ Data is ready! Click 'Next' to configure columns.")

# ============================================
# STEP 2: KEY COLUMNS SELECTION
# ============================================
# ============================================
# STEP 2: KEY COLUMNS SELECTION & DATA TYPE MAPPING
# ============================================
elif st.session_state.step == 2:
    st.subheader("⚙️ Step 2: Configure Columns")
    
    # Check if data is loaded
    if st.session_state.columns_info is None:
        st.error("❌ No data loaded. Please go back to Step 1.")
        if st.button("← Back to Step 1"):
            prev_step()
            st.rerun()
        st.stop()
    
    # Display file info
    file_meta = st.session_state.file_data
    user_input = st.session_state.user_input
    
    st.info(f"📄 **File:** {file_meta['name']}")
    
    # Show data preview
    with st.expander("👁️ Data Preview", expanded=True):
        if st.session_state.df_preview is not None:
            st.dataframe(
                st.session_state.df_preview,
                use_container_width=True,
                height=300
            )
    
    # Show column info
    with st.expander("📊 Column Information", expanded=False):
        import pandas as pd
        
        col_info_list = []
        for col_name, col_info in st.session_state.columns_info.items():
            col_info_list.append({
                'Column': col_name,
                'Type': col_info['inferred_type'],
                'Nulls': f"{col_info['null_count']} ({col_info['null_percentage']}%)",
                'Unique': col_info['unique_count'],
                'Sample': ', '.join(str(v) for v in col_info['sample_values'][:3])
            })
        
        col_info_df = pd.DataFrame(col_info_list)
        st.dataframe(col_info_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # ============================================
    # SECTION 1: KEY COLUMNS SELECTION
    # ============================================
    st.markdown("### 🔑 Select Key Columns")
    st.caption("Key columns uniquely identify each row (like primary keys)")
    
    # Get all column names
    all_columns = list(st.session_state.columns_info.keys())
    
    # Initialize selected_key_columns dari session state (jika ada)
    if 'key_columns' not in st.session_state.user_input:
        st.session_state.user_input['key_columns'] = []
    
    selected_key_columns = []
    
    # Create checkboxes in a grid layout
    num_cols = 3
    cols = st.columns(num_cols)
    
    for idx, col_name in enumerate(all_columns):
        col_info = st.session_state.columns_info[col_name]
        
        # Check if this column was previously selected
        default_checked = col_name in st.session_state.user_input.get('key_columns', [])
        
        # Put checkbox in appropriate column
        with cols[idx % num_cols]:
            is_selected = st.checkbox(
                f"**{col_name}**",
                value=default_checked,
                key=f"key_col_{col_name}",
                help=f"Type: {col_info['inferred_type']} | Unique: {col_info['unique_count']}"
            )
            
            if is_selected:
                selected_key_columns.append(col_name)
    
    st.divider()
    
    # ============================================
    # SECTION 2: DATA TYPE MAPPING (SIMPLIFIED TABULAR)
    # ============================================
    st.markdown("### 🔧 Map Data Types")
    st.caption("Define target data type for each column (leave as 'Default' to use auto-detected type)")
    
    # Available data types untuk mapping
    AVAILABLE_TYPES = [
        "Default",
        "String",
        "Integer", 
        "Long",
        "Float",
        "Double",
        "Decimal",
        "Boolean",
        "Date",
        "Timestamp",
        "Binary"
    ]
    
    # ✅ FIX: Jangan auto-populate, biarkan kosong
    if 'type_mapping' not in st.session_state.user_input:
        st.session_state.user_input['type_mapping'] = {}
    
    # ✅ FIX: Buat temporary dict untuk current session
    current_type_mapping = st.session_state.user_input.get('type_mapping', {})
    
    # Create mapping UI in tabular format
    type_mapping = {}
    
    # Tabular layout dengan 2 kolom
    st.markdown("#### Column Type Configuration")
    
    # Create header
    header_col1, header_col2 = st.columns([2, 1])
    with header_col1:
        st.markdown("**Column Name**")
    with header_col2:
        st.markdown("**Target Type**")
    
    st.markdown("---")
    
    # Create rows
    for col_name in all_columns:
        col_info = st.session_state.columns_info[col_name]
        
        # ✅ FIX: Kalau belum pernah diset, default ke "Default" (index 0)
        # Kalau udah pernah diset, pakai value yang tersimpan
        saved_type = current_type_mapping.get(col_name, "Default")
        
        # Find index
        try:
            current_index = AVAILABLE_TYPES.index(saved_type)
        except ValueError:
            current_index = 0  # Fallback to "Default"
        
        # Create row with 2 columns
        row_col1, row_col2 = st.columns([2, 1])
        
        with row_col1:
            # Show column name with inferred type badge
            inferred_badge = col_info['inferred_type'].capitalize()
            st.markdown(f"**{col_name}** `{inferred_badge}`")
        
        with row_col2:
            # Selectbox for type mapping
            selected_type = st.selectbox(
                f"Type for {col_name}",
                options=AVAILABLE_TYPES,
                index=current_index,  # ✅ Ini akan 0 untuk kolom yang belum pernah diubah
                key=f"type_map_{col_name}",
                label_visibility="collapsed"
            )
            
            # ✅ FIX: Hanya simpan kalau BUKAN "Default"
            if selected_type != "Default":
                type_mapping[col_name] = selected_type
    
    st.divider()
    
    # ============================================
    # PREVIEW: JSON OUTPUT (Only non-default values)
    # ============================================
    with st.expander("👁️ Preview JSON Output", expanded=False):
        import json
        
        # ✅ type_mapping udah otomatis filtered (tidak ada "Default")
        output_json = {
            "key_columns": selected_key_columns,
            "type_mapping": type_mapping,  # Already filtered
        }
        
        # Optional: Add full metadata if needed
        if st.checkbox("Include full column metadata", value=False, key="include_metadata_checkbox"):
            output_json["column_metadata"] = {
                col_name: {
                    "source_type": col_info['dtype'],
                    "inferred_type": col_info['inferred_type'],
                    "target_type": type_mapping.get(col_name, 'Default'),
                    "null_count": col_info['null_count'],
                    "unique_count": col_info['unique_count']
                }
                for col_name, col_info in st.session_state.columns_info.items()
            }
        
        st.json(output_json, expanded=True)
        
        # Show summary stats
        total_cols = len(all_columns)
        custom_cols = len(type_mapping)
        default_cols = total_cols - custom_cols
        
        st.info(f"📊 **Summary:** {total_cols} columns total | {custom_cols} custom types | {default_cols} using default")
        
        # Add download button
        json_str = json.dumps(output_json, indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"column_mapping_{file_meta['name'].split('.')[0]}.json",
            mime="application/json",
            key="download_json_button"
        )
    
    st.divider()
    
    # ============================================
    # NAVIGATION BUTTONS
    # ============================================
    col_back, col_next = st.columns([1, 1])
    
    with col_back:
        back_clicked = st.button("← Back", type="secondary", width='stretch', key="back_step2")
    
    with col_next:
        next_clicked = st.button("Next →", type="primary", width='stretch', key="next_step2")
    
    if back_clicked:
        # Save current selections before going back
        st.session_state.user_input['key_columns'] = selected_key_columns
        st.session_state.user_input['type_mapping'] = type_mapping  # ✅ Hanya non-default
        prev_step()
        st.rerun()
    
    if next_clicked:
        if not selected_key_columns:
            st.error("❌ Please select at least one key column")
        else:
            # Save selected key columns and type mapping
            st.session_state.user_input['key_columns'] = selected_key_columns
            st.session_state.user_input['type_mapping'] = type_mapping  # ✅ Hanya non-default
            
            st.success(f"✅ Configuration saved!")
            st.info(f"🔑 {len(selected_key_columns)} key column(s) | 🔧 {len(type_mapping)} custom type(s)")
            
            # Move to next step
            next_step()
            st.rerun()
# ============================================
# STEP 3: ADDITIONAL CONFIGURATIONS (Placeholder)
# ============================================
elif st.session_state.step == 3:
    st.subheader("🎯 Step 3: Finalize Configuration")
    
    # st.info("🚧 This step is under construction")
    fabric_options = ["SILVER_LH_MCUADMIN_MCU_ADMIN-SILVER", 
                      "SILVER_LH_HIS_IMPORT-SILVER", 
                      "SILVER_LH_SPECTRA", 
                      "SILVER_LH_P_FINANCE_DEV"]
    st.markdown("### 📍 Destination")
    # target_destination = st.text_input("Target Destination", key="key_target_destination")
    if 'dest_config' not in st.session_state.user_input:
        st.session_state.user_input['dest_config'] = {
            'target_dest': fabric_options[0] if fabric_options else "",
            'table_name': '',
            'pic_name': ''
        }
    dest_val = st.session_state.user_input['dest_config']
    with st.container(border=True):
        st.markdown("### 🏢 Target Destination")
        
        # Target Destination (Searchable Dropdown)
        # index=[...].index() digunakan agar pilihan user 'nempel' saat bolak-balik page
        target_destination = st.selectbox(
            "Target Destination (Search & Select)*",
            options=fabric_options,
            index=fabric_options.index(dest_val['target_dest']) if dest_val['target_dest'] in fabric_options else 0,
            help="Type to search: e.g. 'Marketing', 'Finance', 'Legacy_DB'",
            key="sb_target_dest"
        )
        st.caption("ℹ️ *Search by typing the name in the box above*")

        # Final Table Name
        table_name = st.text_input(
            "Final Table Name*",
            value=dest_val['table_name'],
            placeholder="e.g., stg_sales_report_daily",
            help="This name will be used as the table name in the target database",
            key="ti_table_name"
        )

        # Configurator Name (PIC)
        pic_name = st.text_input(
            "Configurator Name (PIC)*",
            value=dest_val['pic_name'],
            placeholder="e.g., Jono Sudibyo",
            key="ti_pic_name"
        )
    st.divider()
    # Show summary
    st.markdown("### 📋 Configuration Summary")
    
    user_input = st.session_state.user_input
    
    # st.subheader("📝 Final Review")
    st.caption("Please double-check all configurations before submitting.")

    # Membuat 3 kolom agar seimbang
    summ_col1, summ_col2 = st.columns(2)

    with summ_col1:
        st.markdown("##### 📂 Source Info")
        # Gunakan styling yang konsisten
        st.info(f"""
        **Folder:** `{user_input.get('folder_path')}`  
        **File:** `{user_input.get('file_name')}`  
        **Sheet:** `{user_input.get('sheet_name') or 'Default'}`
        """)

    with summ_col2:
        st.markdown("##### 🔑 Key & Schema")
        # Ambil info key columns
        keys = user_input.get('key_columns', [])
        key_text = ", ".join(keys) if keys else "None selected"
        
        # Hitung total kolom dari columns_info
        total_cols = len(st.session_state.columns_info) if st.session_state.columns_info is not None else 0
        
        st.success(f"""
        **Total Columns:** `{total_cols}`  
        **Primary Keys:** `{key_text}`
        """)


    st.markdown("##### 🎯 Destination")
    # Ambil data dari dest_config yang kita buat tadi
    dest = user_input.get('dest_config', {})
    
    st.warning(f"""
    **Target:** `{target_destination}`  
    **Table:** `{table_name if table_name else 'Wait for input...'}`  
    **PIC:** `{pic_name if pic_name else 'Wait for input...'}`
    """)
    
    st.divider()
    
    col_back, col_submit, col_reset = st.columns([1, 1, 1])
    
    with col_back:
        if st.button("← Back", type="secondary", width='stretch'):
            st.session_state.user_input['dest_config'] = {
            'target_dest': target_destination,
            'table_name': table_name,
            'pic_name': pic_name
            }
            prev_step()
            st.rerun()
    
    with col_submit:
        if st.button("🚀 Submit to Fabric", type="primary", width='stretch'):
            st.session_state.user_input['dest_config'] = {
            'target_dest': target_destination,
            'table_name': table_name,
            'pic_name': pic_name
            }
            st.success("✅ Configuration submitted!")
            st.balloons()
            # TODO: Send to Fabric Pipeline here
    
    with col_reset:
        if st.button("🔄 Start Over", type="secondary", width='stretch'):
            reset_app()
            st.rerun()

# ============================================
# SIDEBAR - Debug Info (Optional)
# ============================================
with st.sidebar:
    st.markdown("### 🔍 Debug Info")
    st.write(f"Current Step: {st.session_state.step}")
    st.write(f"Data Fetched: {'Yes' if st.session_state.data_fetched else 'No'}")  # ✅ UBAH
    st.write(f"Data Loaded: {'Yes' if st.session_state.columns_info else 'No'}")
    
    if st.session_state.columns_info:
        st.write(f"Total Columns: {len(st.session_state.columns_info)}")
    
    # ✅ TAMBAHAN: Show selected key columns
    if st.session_state.user_input.get('key_columns'):
        st.write(f"Key Columns Selected: {len(st.session_state.user_input['key_columns'])}")
    
    if st.button("🔄 Reset App"):
        reset_app()
        st.rerun()