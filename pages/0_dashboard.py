import streamlit as st
import st_supabase_connection

st_supabase_connection.query("*", table="countries", ttl=0).execute()