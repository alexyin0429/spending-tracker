import streamlit as st
import pandas as pd
import numpy as np
import json
import uuid
from st_supabase_connection import SupabaseConnection

def file_uploader(expected_file_type: list):
    st.write("Upload a bank statement file")
    bank_options = ["BMO", "CIBC"]
    card_options = ["Credit Card", "Debit Card"]
    person_options = ["ywl", "skx"]
    uploaded_file = st.file_uploader("Choose a file", type=expected_file_type)
    bank_selected = st.selectbox("For Which Bank?", bank_options)
    card_selected = st.selectbox("For Which Card?", card_options)
    person_selected = st.selectbox("For Which Person?", person_options)
    submit_button = st.button("Submit")
    if bank_selected not in bank_options or card_selected not in card_options:
        st.error("Bank and/or card not valid!", icon="⛔️")
    else:
        if uploaded_file is not None and submit_button:
            st.success("File Upload Successfully!", icon="✅")
            if bank_selected == "CIBC":
                df = pd.read_csv(uploaded_file, header=None)
            else:
                if card_selected == 'Debit':
                    df = pd.read_csv(uploaded_file, skiprows=1)
                else:
                    df = pd.read_csv(uploaded_file, skiprows=2)
            return df, bank_selected, card_selected, person_selected
        elif uploaded_file is None and submit_button:
            st.error("File Not Found!", icon="⛔️")


def data_cleaning(df, bank, card, person):
    if bank == "BMO":
        if card == "Credit Card":
            return _data_cleaning_for_bmo_credit(df, person)
        else:
            return _data_cleaning_for_bmo_debit(df, person)
    else:
        return _data_cleaning_for_cibc_credit(df)

def _data_cleaning_for_bmo_debit(df, person):
    transaction_amount_column = ' Transaction Amount'
    df['transaction_amount'] = df[transaction_amount_column]
    df = df.rename(columns={'Date Posted': 'date', 'Description': 'description'})
    df['date'] = pd.to_datetime(df['date'].astype('str'), format='%Y%m%d').dt.strftime('%Y-%m-%d')
    # Initialize 'comment', 'label', and 'bank' columns to empty strings
    df['comment'] = '.'
    df['label'] = '.'
    df['bank'] = person + ' bmo debit'
    df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
    # Selecting and reordering the required columns
    df = df[['id','label', 'date', 'description', 'transaction_amount', 'comment', 'bank']]
    return df

def _data_cleaning_for_bmo_credit(df, person):
    df = df.rename(columns={'Transaction Date': 'date', 'Transaction Amount': 'transaction_amount', 'Description': 'description'})

    # Convert 'date' from integer to datetime format
    df['date'] = pd.to_datetime(df['date'].astype('str'), format='%Y%m%d').dt.strftime('%Y-%m-%d')
    # Adjust 'transaction_amount' to be positive for income and negative for spending
    df['transaction_amount'] = df['transaction_amount'] * -1
    # Initialize 'comment', 'label', and 'bank' columns to empty strings
    df['comment'] = '.'
    df['label'] = '.'
    df['bank'] = person + ' bmo credit'
    df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
    # Selecting and reordering the required columns
    df = df[['id', 'label', 'date', 'description', 'transaction_amount', 'bank', 'comment']]
    return df

def _data_cleaning_for_cibc_credit(df):
    df.columns = ['date', 'description', 'Spending', 'Income', 'Card']
    # Calculate 'transaction_amount' from 'Spending' and 'Income'
    df['transaction_amount'] = np.where(df['Income'].isna(), -df['Spending'], df['Income'])
    # Drop the 'Card', 'Spending', and 'Income' columns
    df = df.drop(columns=['Card', 'Spending', 'Income'])
    # Initialize 'comment', 'label', and 'bank' columns to empty strings
    df['comment'] = '.'
    df['label'] = '.'
    df['bank'] = 'CIBC'
    df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
    # Selecting and reordering the required columns
    df = df[['id', 'label', 'date', 'description', 'transaction_amount', 'bank', 'comment']]
    return df

def db_connection():
    st_supabase_client = st.connection(
        name="supabase",
        type=SupabaseConnection,
        ttl=None,
        url=st.secrets['SUPABASE_URL'],
        key=st.secrets['SUPABASE_KEY']
    )
    return st_supabase_client

def convert_df_to_json(df):
    return [record for record in df.to_dict(orient='records')]

def db_save(df, table_name):
    conn = db_connection()
    data, count = conn.table(table_name).insert(convert_df_to_json(df),
                                  count="None").execute()
    return data, count

def db_get_all_labels():
    conn = db_connection()
    data, count = conn.query("name", table="label_type").execute()
    df = pd.DataFrame([d['name'] for d in data[1]]).T
    df.columns = range(1, len(data[1]) + 1)
    return df

def form_submitted():
    st.session_state.form_submitted = True

def form_reset():
    st.session_state.edited_df = None
    st.session_state.form_submitted = False

def save_edited_df():
    st.session_state.edited_df = st.session_state.temp_edited_df

def reset_edited_df():
    st.session_state.edited_df = None