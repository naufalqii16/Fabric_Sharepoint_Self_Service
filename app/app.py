import streamlit as st
import os
import sys
import json
from io import BytesIO

# --- 1. SETUP PATH & IMPORTS ---
current_file = os.path.abspath(__file__)
app_dir = os.path.dirname(current_file)
root_dir = os.path.dirname(app_dir)

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import services
from services.config import *
from services.auth import auth
from services.sharepoint_services import SharePointService
from services.preprocessing import process_file_to_dataframe, extract_columns_metadata

st.set_page_config(page_title="Excel Ingestion Configurator", layout="wide")

# --- 2. INITIALIZATION ---
if 'step' not in st.session_state:
    st.session_state.step = 1

if 'input_data' not in st.session_state:
    st.session_state.input_data = {
        'sp_url': '', 'file_name': '', 'folder_path': '', 'extension': '.xlsx',
        'delimiter': 'comma', 'sheet_name': '', 'header_row': 1,
        'selected_options': {
            'read_data': True, 'clean_columns': True, 'remove_blank_rows': True,
            'drop_unnamed_columns': True, 'update_df_dtypes': True, 'choose_column': True,
            'load_silver_table': True, 'add_or_update_load_at': False,
            'remove_blank_columns': False, 'remove_specific_rows': False, 'delete_file': False
        }
    }

sp_service = SharePointService(site_id=SITE_ID, drive_id=DRIVE_ID)

# --- 3. UI HEADER ---
st.title("⚙️ Configuration Panel")
progress_mapping = {1: 0.33, 2: 0.66, 3: 1.0}
st.progress(progress_mapping.get(st.session_state.step, 1.0))

# --- 4. STEP 1: SOURCE & FILE ---
if st.session_state.step == 1:
    st.subheader("📍 Source & File")
    
    sp_url = st.text_input("Sharepoint URL**", value=st.session_state.input_data['sp_url'], key="saved_sp_url")
    folder_path = st.text_input("Folder Path**", value=st.session_state.input_data['folder_path'], key="saved_folder_path")

    col1, col2 = st.columns(2)
    with col1:
        file_name = st.text_input("File Name**", value=st.session_state.input_data['file_name'], key="saved_file_name")
    with col2:
        extension = st.selectbox("Extension", options=[".xlsx", ".csv"], 
                                 index=0 if st.session_state.input_data['extension'] == ".xlsx" else 1)
    
    delimiter = "NULL"
    if extension == ".csv":
        delimiter = st.selectbox("Delimiter", options=["comma", "semicolon", "tab", "pipe", "NULL"])

    col3, col4 = st.columns(2)
    with col3:
        sheet_name = st.text_input("Sheet Name**", value=st.session_state.input_data['sheet_name'])
    with col4:
        header_row = st.number_input("Header Row Index", min_value=1, value=st.session_state.input_data['header_row'])
    
    st.divider()
    if st.button("Next (⚙️ Actions & Rules) ➡️", key="next_1", type="primary"):
        if sp_url and file_name and sheet_name:
            # Simpan ke session state
            st.session_state.input_data.update({
                'sp_url': sp_url, 'file_name': file_name, 'folder_path': folder_path,
                'extension': extension, 'sheet_name': sheet_name, 
                'header_row': header_row, 'delimiter': delimiter
            })
            st.session_state.step = 2
            st.rerun()
        else:
            st.error("💡 Please fill all mandatory fields (URL, File Name, Sheet Name)")

# --- 5. STEP 2: ACTIONS & RULES ---
elif st.session_state.step == 2:
    st.subheader("⚙️ Actions & Rules")
    
    # Debug info (optional)
    st.sidebar.write(f"📂 Folder: {st.session_state.input_data['folder_path']}")
    st.sidebar.write(f"📄 File: {st.session_state.input_data['file_name']}")

    st.write("Actions To Perform:")
    opts = st.session_state.input_data['selected_options']
    
    col_a, col_b = st.columns(2)
    with col_a:
        a1 = st.checkbox("read_data", value=opts['read_data'], key="chk_1")
        a2 = st.checkbox("clean_columns", value=opts['clean_columns'], key="chk_2")
        a3 = st.checkbox("remove_blank_rows", value=opts['remove_blank_rows'], key="chk_3")
        a4 = st.checkbox("drop_unnamed_columns", value=opts['drop_unnamed_columns'], key="chk_4")
        a5 = st.checkbox("update_df_dtypes", value=opts['update_df_dtypes'], key="chk_5")
        a6 = st.checkbox("choose_column", value=opts['choose_column'], key="chk_6")
        a7 = st.checkbox("load_silver_table", value=opts['load_silver_table'], key="chk_7")

    with col_b:
        a8 = st.checkbox("add_or_update_load_at", value=opts['add_or_update_load_at'], key="chk_8")
        a9 = st.checkbox("remove_blank_columns", value=opts['remove_blank_columns'], key="chk_9")
        a10 = st.checkbox("remove_specific_rows", value=opts['remove_specific_rows'], key="chk_10")
        a11 = st.checkbox("delete_file", value=opts['delete_file'], key="chk_11")

    st.divider()
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⬅️ Back", key="back_2"):
            st.session_state.step = 1
            st.rerun()
    with nav2:
        if st.button("Next (🎯 Destination) ➡️", key="next_2", type="primary"):
            # Update dictionary selected_options
            st.session_state.input_data['selected_options'] = {
                'read_data': a1, 'clean_columns': a2, 'remove_blank_rows': a3,
                'drop_unnamed_columns': a4, 'update_df_dtypes': a5, 'choose_column': a6,
                'load_silver_table': a7, 'add_or_update_load_at': a8,
                'remove_blank_columns': a9, 'remove_specific_rows': a10, 'delete_file': a11
            }
            st.session_state.step = 3
            st.rerun()

# --- 6. STEP 3: DESTINATION ---
elif st.session_state.step == 3:
    st.subheader("🎯 Destination")
    st.write("Summary of your configuration:")
    st.json(st.session_state.input_data)
    
    if st.button("⬅️ Back to Rules", key="back_3"):
        st.session_state.step = 2
        st.rerun()

# --- DEBUG SIDEBAR ---
st.sidebar.divider()
st.sidebar.write(f"Current Step: {st.session_state.step}")
if st.sidebar.button("Reset App"):
    st.session_state.step = 1
    st.rerun()