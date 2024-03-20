import streamlit as st
from streamlit.logger import get_logger
from streamlit_extras.switch_page_button import switch_page
from st_supabase_connection import SupabaseConnection



LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )

    if st.button('Upload Transactions'):
        switch_page('upload_transactions')
    

if __name__ == "__main__":
    run()
