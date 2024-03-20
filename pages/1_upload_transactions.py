import streamlit as st
import pandas as pd
from utils import file_uploader, data_cleaning, db_save, db_get_all_labels
from streamlit_extras.switch_page_button import switch_page
from st_supabase_connection import SupabaseConnection

def upload_transaction():
    uploaded_file = file_uploader(['csv'])
    if uploaded_file is not None:
        data = uploaded_file[0]
        bank = uploaded_file[1]
        card = uploaded_file[2]
        person = uploaded_file[3]
        data_clean = data_cleaning(data, bank, card, person)
        return data_clean
    return pd.DataFrame(columns=['id', 'label', 'date', 'description', 'transaction_amount', 'bank', 'comment'])
           
st.session_state.uploaded_df = upload_transaction()

labels = db_get_all_labels()
st.data_editor(labels)

edited_ef = st.session_state.uploaded_df
st.data_editor(edited_ef)
# print(edited_df)
#     st.data_editor(st.session_state.uploaded_df, disabled=True)
#     edit = st.button("Edit", key="button")
#     print("Edit: ")
#     print(edit)
#     if edit:
#         form = st.form("label form", key="label_form")
#         edited_df = form.data_editor(st.session_state.uploaded_df, num_rows="dynamic")
#         st.session_state.submitted = form.form_submit_button("Ready to Save")
#         if st.session_state.submitted:
#             data, count = db_save(edited_df, "transaction")
#             if data != []:
#                 st.success("Saved Successfully!")

#     data, count = db_save(st.session_state.edited_df, "transaction")
#     if data != []:
#         st.success("Saved Successfully!")
# print(st.session_state.temp_edited_df['label'])

    

if st.button("Back to Dashboard"):
    switch_page("dashboard")