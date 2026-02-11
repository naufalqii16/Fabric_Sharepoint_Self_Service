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

def process_user_input():
    """
    Backend processing: Read file from SharePoint and extract column metadata
    This runs when user clicks 'Next' on Step 1
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
    
    with st.form("step1_form"):
        st.text("Source Location")
        
        # SharePoint URL (optional for display)
        sp_url = st.text_input(
            "Sharepoint URL (optional)", 
            placeholder="https://yourcompany.sharepoint.com/...",
            help="This is for reference only"
        )
        
        # Folder Path (required)
        folder_path = st.text_input(
            "Folder Path*",
            placeholder="e.g., Fabric_Excel_Files/Test_Excel",
            help="Path to the folder in SharePoint"
        )
        
        # File details
        col1, col2 = st.columns(2)
        with col1:
            file_name = st.text_input(
                "File Name*",
                placeholder="e.g., Online Retail.xlsx",
                help="Exact filename including extension"
            )
        with col2:
            extension = st.selectbox(
                "Extension",
                [".xlsx", ".xls", ".csv"],
                help="File type"
            )
        
        # CSV-specific options
        delimiter = None
        custom_delimiter = None
        if extension == ".csv":
            c1, c2 = st.columns(2)
            with c1:
                delimiter = st.selectbox("Delimiter", [",", ";", "\t", "|", "Custom"])
            with c2:
                if delimiter == "Custom":
                    custom_delimiter = st.text_input("Input Custom Delimiter")
                    if not custom_delimiter:
                        st.warning("⚠️ Custom delimiter cannot be empty!")
        
        # Additional file options
        col3, col4, col5 = st.columns(3)
        
        with col3:
            sheet_name = st.text_input(
                "Sheet Name",
                placeholder="Leave empty for first sheet",
                help="For Excel files only"
            )
        
        with col4:
            header_row = st.number_input(
                "Header Row Index",
                min_value=0,
                value=0,
                help="Row index where column headers are (0-indexed)"
            )
        
        with col5:
            need_backup = st.checkbox(
                "Create Backup",
                value=False,
                help="Create backup copy before reading"
            )
        
        st.divider()
        
        # Validation
        mandatory_fields = [folder_path, file_name]
        
        # Submit button
        submitted = st.form_submit_button("🔍 Fetch File & Next", type="primary")
        
        if submitted:
            if not all(mandatory_fields):
                st.error("❌ Please fill all mandatory fields marked with *")
            elif extension == ".csv" and delimiter == "Custom" and not custom_delimiter:
                st.error("❌ Please provide custom delimiter")
            else:
                # Save user input to session state
                st.session_state.user_input = {
                    'sp_url': sp_url,
                    'folder_path': folder_path,
                    'file_name': file_name,
                    'extension': extension,
                    'delimiter': custom_delimiter if delimiter == "Custom" else delimiter,
                    'sheet_name': sheet_name,
                    'header_row': header_row,
                    'need_backup': need_backup
                }
                
                # Process file and extract columns
                success = process_user_input()
                
                if success:
                    # Move to next step
                    next_step()
                    st.rerun()

# ============================================
# STEP 2: KEY COLUMNS SELECTION
# ============================================
elif st.session_state.step == 2:
    st.subheader("⚙️ Step 2: Configure Key Columns")
    
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
    
    # Key columns selection form
    with st.form("step2_form"):
        st.markdown("### 🔑 Select Key Columns")
        st.caption("Key columns uniquely identify each row (like primary keys)")
        
        # Get all column names
        all_columns = list(st.session_state.columns_info.keys())
        
        # Create checkboxes in a grid layout
        num_cols = 3
        cols = st.columns(num_cols)
        
        selected_key_columns = []
        
        for idx, col_name in enumerate(all_columns):
            col_info = st.session_state.columns_info[col_name]
            
            # Put checkbox in appropriate column
            with cols[idx % num_cols]:
                is_selected = st.checkbox(
                    f"**{col_name}**",
                    key=f"key_col_{col_name}",
                    help=f"Type: {col_info['inferred_type']} | Unique: {col_info['unique_count']}"
                )
                
                if is_selected:
                    selected_key_columns.append(col_name)
                
                # Show sample values under checkbox
                st.caption(f"📝 {', '.join(str(v) for v in col_info['sample_values'][:2])}")
        
        st.divider()
        
        # Navigation buttons
        col_back, col_next = st.columns([1, 1])
        
        with col_back:
            back_clicked = st.form_submit_button("← Back", type="secondary")
        
        with col_next:
            next_clicked = st.form_submit_button("Next →", type="primary")
        
        if back_clicked:
            prev_step()
            st.rerun()
        
        if next_clicked:
            if not selected_key_columns:
                st.error("❌ Please select at least one key column")
            else:
                # Save selected key columns
                st.session_state.user_input['key_columns'] = selected_key_columns
                
                st.success(f"✅ Selected {len(selected_key_columns)} key column(s): {', '.join(selected_key_columns)}")
                
                # Move to next step
                next_step()
                st.rerun()

# ============================================
# STEP 3: ADDITIONAL CONFIGURATIONS (Placeholder)
# ============================================
elif st.session_state.step == 3:
    st.subheader("🎯 Step 3: Finalize Configuration")
    
    st.info("🚧 This step is under construction")
    
    # Show summary
    st.markdown("### 📋 Configuration Summary")
    
    user_input = st.session_state.user_input
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📂 Source:**")
        st.write(f"- Folder: `{user_input.get('folder_path')}`")
        st.write(f"- File: `{user_input.get('file_name')}`")
        st.write(f"- Sheet: `{user_input.get('sheet_name') or 'First sheet'}`")
    
    with col2:
        st.markdown("**🔑 Key Columns:**")
        for col in user_input.get('key_columns', []):
            st.write(f"- {col}")
    
    st.divider()
    
    col_back, col_submit, col_reset = st.columns([1, 1, 1])
    
    with col_back:
        if st.button("← Back", type="secondary"):
            prev_step()
            st.rerun()
    
    with col_submit:
        if st.button("🚀 Submit to Fabric", type="primary"):
            st.success("✅ Configuration submitted!")
            st.balloons()
            # TODO: Send to Fabric Pipeline here
    
    with col_reset:
        if st.button("🔄 Start Over", type="secondary"):
            reset_app()
            st.rerun()

# ============================================
# SIDEBAR - Debug Info (Optional)
# ============================================
with st.sidebar:
    st.markdown("### 🔍 Debug Info")
    st.write(f"Current Step: {st.session_state.step}")
    st.write(f"Data Loaded: {'Yes' if st.session_state.columns_info else 'No'}")
    
    if st.session_state.columns_info:
        st.write(f"Total Columns: {len(st.session_state.columns_info)}")
    
    if st.button("🔄 Reset App"):
        reset_app()
        st.rerun()