import streamlit as st
import pandas as pd

def file_uploader(expected_file_type: list):
    st.write("Upload a bank statement file")
    bank_options = ["BMO", "CIBC"]
    card_options = ["Credit Card", "Debit Card"]
    uploaded_file = st.file_uploader("Choose a file", type=expected_file_type)
    bank_selected = st.selectbox("For Which Bank?", bank_options)
    card_selected = st.selectbox("For Which Card?", card_options)
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
            return df, bank_selected, card_selected
        elif uploaded_file is None and submit_button:
            st.error("File Not Found!", icon="⛔️")


def data_cleaning(df, bank, card):
    if bank == "BMO":
        if card == "Credit Card":
            return _data_cleaning_for_bmo_credit(df)
        else:
            return _data_cleaning_for_bmo_debit(df)
    else:
        return _data_cleaning_for_cibc_credit(df)

def _data_cleaning_for_bmo_debit(df):
    transaction_amount_column = ' Transaction Amount'
    df['Spending'] = 0.0
    df['Income'] = 0.0
    df.loc[df['Transaction Type'] == 'DEBIT', 'Spending'] = -df[transaction_amount_column]
    df.loc[df['Transaction Type'] == 'CREDIT', 'Income'] = df[transaction_amount_column]
    df = df.rename(columns={'Transaction Type': 'Transaction_Type', 
                            'Date Posted': 'Date', 
                            ' Transaction Amount': 'Amount', 
                            'Description': 'Description'})
    # Convert 'Date' from integer to datetime format
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
    # Reordering columns to match the requested format
    df = df[['Date', 'Description', 'Spending', 'Income']]
    return df

def _data_cleaning_for_bmo_credit(df):
    # Rename and select relevant columns
    df = df.rename(columns={'Transaction Date': 'Date', 
                            'Transaction Amount': 'Amount'})
    # Convert 'Date' from integer to datetime format
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
    # Creating 'Spending' and 'Income' columns based on 'Amount'
    df['Spending'] = df['Amount'].apply(lambda x: x if x > 0 else 0)
    df['Income'] = df['Amount'].apply(lambda x: -x if x < 0 else 0)
    # Reordering columns to match the requested format
    df = df[['Date', 'Description', 'Spending', 'Income']]
    return df

def _data_cleaning_for_cibc_credit(df):
    df.columns = ['Date', 'Description', 'Spending', 'Income', 'Card']
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    # Drop the 'Card' column
    df = df.drop(columns=['Card'])

    # Select only the required columns
    df = df[['Date', 'Description', 'Spending', 'Income']]
    return df