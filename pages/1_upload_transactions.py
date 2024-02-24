import time

import numpy as np

import streamlit as st
from streamlit.hello.utils import show_code
from utils import file_uploader, data_cleaning

def dashboard():
    uploaded_file = file_uploader(['csv'])
    if uploaded_file is not None:
        data = uploaded_file[0]
        bank = uploaded_file[1]
        card = uploaded_file[2]
        data_clean = data_cleaning(data, bank, card)
        if not (data_clean.empty):
            st.download_button(
                label="Download data as CSV",
                data=data_clean.to_csv().encode('utf-8'),
                file_name=f'{bank}_{card}_transactions.csv',
                mime='text/csv',)
