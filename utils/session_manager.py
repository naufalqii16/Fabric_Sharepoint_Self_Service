from typing import Optional, Dict, Any
import pandas as pd
import streamlit as st

class SessionManager:
    """Centralized session state management"""
    
    # Keys untuk session state
    CURRENT_PAGE = 'current_page'
    RAW_DATA = 'raw_df'
    COLUMNS_INFO = 'columns_info'
    FILE_METADATA = 'file_metadata'
    INPUT_PARAMS = 'input_params'
    IS_DATA_LOADED = 'is_data_loaded'
    
    @staticmethod
    def init():
        """Initialize default session state"""
        defaults = {
            SessionManager.CURRENT_PAGE: 1,
            SessionManager.IS_DATA_LOADED: False,
            SessionManager.RAW_DATA: None,
            SessionManager.COLUMNS_INFO: {},
            SessionManager.FILE_METADATA: {},
            SessionManager.INPUT_PARAMS: {}
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    @staticmethod
    def save_page1_data(df: pd.DataFrame, columns_info: dict, 
                        file_metadata: dict, input_params: dict):
        """Save data from Page 1 processing"""
        # IMPORTANT: Untuk file besar, jangan save full DataFrame
        # Cukup save sample + row count
        if len(df) > 1000:
            st.session_state[SessionManager.RAW_DATA] = df.head(1000)  # Sample only
            st.session_state[SessionManager.FILE_METADATA]['total_rows'] = len(df)
            st.session_state[SessionManager.FILE_METADATA]['is_sampled'] = True
        else:
            st.session_state[SessionManager.RAW_DATA] = df
            st.session_state[SessionManager.FILE_METADATA]['is_sampled'] = False
        
        st.session_state[SessionManager.COLUMNS_INFO] = columns_info
        st.session_state[SessionManager.FILE_METADATA] = file_metadata
        st.session_state[SessionManager.INPUT_PARAMS] = input_params
        st.session_state[SessionManager.IS_DATA_LOADED] = True
    
    @staticmethod
    def get_df() -> Optional[pd.DataFrame]:
        """Get stored DataFrame"""
        return st.session_state.get(SessionManager.RAW_DATA)
    
    @staticmethod
    def get_columns_info() -> dict:
        """Get columns metadata"""
        return st.session_state.get(SessionManager.COLUMNS_INFO, {})
    
    @staticmethod
    def is_ready_for_page2() -> bool:
        """Check if data is ready for Page 2"""
        return st.session_state.get(SessionManager.IS_DATA_LOADED, False)
    
    @staticmethod
    def navigate_to(page_num: int):
        """Navigate to specific page"""
        st.session_state[SessionManager.CURRENT_PAGE] = page_num
        st.rerun()
    
    @staticmethod
    def reset():
        """Clear all session data"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        SessionManager.init()