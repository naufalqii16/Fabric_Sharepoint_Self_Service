import streamlit as st

st.set_page_config(page_title="Excel Ingestion Configurator", layout="wide")

st.title("⚙️ Configuration Panel")
st.caption("Input the needed config here")

if 'input_data' not in st.session_state:
    # Buat dictionary kosong untuk menampung semua field kamu
    st.session_state.input_data = {
        'sp_url': '',
        'file_name': '',
        'folder_path': '',
        'extension': '',
        'delimiter': '',
        'custom_delimiter': '',
        'sheet_name': '',
        'key_col': '',
        'header_row': 1,
        'pic_name': '',
        'target': '',
        'table_name': '',
        'selected_options': {
            'Option 1': True, 'Option 2': True, 'Option 3': True,
            'Option 4': True, 'Option 5': True, 'Option 6': True,
            'Option 7': True, 'Option 8': False, 'Option 9': False,
            'Option 10': False, 'Option 11': False
        }
    }

# tab1, tab2, tab3 = st.tabs(["📍 Source & File", "⚙️ Actions & Rules", "🎯 Destination"])
if 'step' not in st.session_state:
    st.session_state.step = 1
def next_step():
    st.session_state.step +=1

def prev_step():
    st.session_state.step -=1

progress_mapping = {1: 0.33, 2: 0.66, 3: 1.0}
st.progress(progress_mapping[st.session_state.step])

# with tab1:
if st.session_state.step == 1:
    st.subheader("📍 Source & File")
    st.text("Source Location")
    
    sp_url = st.text_input("Sharepoint URL**", value=st.session_state.input_data['sp_url'],placeholder="https://...", key="saved_sp_url")
    folder_path = st.text_input("Folder Path**", value=st.session_state.input_data['folder_path'],  key="saved_folder_path")

    col1, col2 = st.columns(2)
    with col1:
        file_name = st.text_input("File Name**", value=st.session_state.input_data['file_name'], key= "saved_file_name")
    with col2:
        options_extension = [".xlsx", ".csv"]
        saved_ext = st.session_state.input_data['extension']
        try:
            idx_ext = options_extension.index(saved_ext)
        except ValueError:
            idx_ext = 0
        extension= st.selectbox("Extension", options=options_extension, index=idx_ext, key="saved_extension")
    
    if extension == ".csv":
        c1, c2 = st.columns(2)
        with c1:
            options_delimiter = ["NULL", ",", ";", "Custom"]
            saved_del = st.session_state.input_data['delimiter']
            try:
                idx_del = options_delimiter.index(saved_del)
            except ValueError:
                idx_del = 0
            delimiter = st.selectbox("Delimiter", options=options_delimiter , key="saved_delimiter")
        with c2:
            if delimiter == "Custom":
                custom_delimiter = st.text_input("Input Custom Delimiter", key="saved_custom_delimiter")
                if not custom_delimiter:
                    st.error("Custom delimiter cannot be empty if you choose 'Custom'!")
    
    col3, col4 = st.columns(2)

    with col3:
        sheet_name = st.text_input("Sheet Name**", value=st.session_state.input_data['sheet_name'], key="saved_sheet_name")
    # with col4:
    #     key_col = st.text_input("Key Column**", placeholder="e.g. user_id, email, region", key="saved_key_column")
    #     st.caption("Use comma as a delimiter if more than one key")
    with col4:
        header_row = st.number_input("Header Row Index", min_value=1, value=st.session_state.input_data['header_row'], key="saved_row_index")
    
    st.divider()
    mandatory_fields1 = [sp_url, file_name, sheet_name]

    if all(mandatory_fields1):
        # st.button("Next", on_click=next_step)
        if st.button("Next"):
            st.session_state.input_data['sp_url'] = sp_url
            st.session_state.input_data['file_name'] = file_name
            st.session_state.input_data['folder_path'] = folder_path
            st.session_state.input_data['extension'] = extension
            st.session_state.input_data['sheet_name'] = sheet_name
            st.session_state.input_data['header_row'] = header_row
            if extension ==".csv":
                st.session_state.input_data['delimiter'] = delimiter
            else:
                st.session_state.input_data['delimiter'] = "NULL"

            st.session_state.step = 2
            st.rerun()
    else:
        st.info("💡Please fill all the mandatory fields")
    # st.sidebar.json(st.session_state)

elif st.session_state.step ==2:

    st.subheader("⚙️ Actions & Rules")
    st.text("Advanced Settings")

    need_backup = st.radio("Need to Backup?", ["Yes", "No"], horizontal=True)
    st.write("Actions To Perform:")
    
    col_a, col_b = st.columns(2)
    with col_a:
        a1= st.checkbox("read_data", value=True)
        a2= st.checkbox("clean_columns", value=True)
        a3= st.checkbox("remove_blank_rows", value=True)
        a4= st.checkbox("drop_unnamed_columns", value=True)
        a5= st.checkbox("update_df_dtypes", value=True)
        a6= st.checkbox("choose_column", value=True)
        a7= st.checkbox("load_silver_table", value=True)
    with col_b:
        a8= st.checkbox("add_or_update_load_at")
        a9= st.checkbox("remove_blank_columns")
        a10= st.checkbox("remove_specific_rows")
        a11= st.checkbox("delete_file")
    st.info("Action 1-7 are default mandatory actions, if you want to skip a mandatory action, you can uncheck the box")

    st.divider()
    col_nav1, col_nav2 = st.columns([1,1], gap="large")
    with col_nav1:
        st.button("Back", on_click=prev_step, use_container_width=True)
    with col_nav2:
        st.button("Next", on_click=next_step, use_container_width=True)

elif st.session_state.step == 3:
    st.subheader("🎯 Destination")
        


