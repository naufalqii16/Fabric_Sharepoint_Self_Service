import streamlit as st

st.set_page_config(page_title="Excel Ingestion Configurator", layout="wide")

st.title("⚙️ Configuration Panel")
st.caption("Input the needed config here")

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
    sp_url = st.text_input("Sharepoint URL**", placeholder="https://...")
    folder_path = st.text_input("Folder Path**")

    col1, col2 = st.columns(2)
    with col1:
        file_name = st.text_input("File Name**")
    with col2:
        extension= st.selectbox("Extension", [".xlsx", ".csv"])
    
    if extension == ".csv":
        c1, c2 = st.columns(2)
        with c1:
            delimiter = st.selectbox("Delimiter", ["NULL", ",", ";", "Custom"])
        with c2:
            if delimiter == "Custom":
                custom_delimiter = st.text_input("Input Custom Delimiter")
                if not custom_delimiter:
                    st.error("Custom delimiter cannot be empty if you choose 'Custom'!")
    
    col3, col4, col5 = st.columns(3)

    with col3:
        sheet_name = st.text_input("Sheet Name**")
    with col4:
        key_col = st.text_input("Key Column**", placeholder="e.g. user_id, email, region")
        st.caption("Use comma as a delimiter if more than one key")
    with col5:
        header_row = st.number_input("Header Row Index", min_value=1, value=1)
    
    st.divider()
    mandatory_fields1 = [sp_url, file_name, sheet_name, key_col]

    if all(mandatory_fields1):
        st.button("Next", on_click=next_step)
    else:
        st.info("💡Please fill all the mandatory fields")
if st.session_state.step ==2:

    st.subheader("⚙️ Actions & Rules")
    st.text("Advan")

