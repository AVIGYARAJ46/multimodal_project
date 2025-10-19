import streamlit as st
from database import init_db  # ✅ Ensure database is created before using

# --- Streamlit setup ---
st.set_page_config(page_title="Multimodal Q&A Assistant", layout="wide")

# Initialize the database once at app startup
init_db()

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["File Upload and Extraction", "View Stored Data"])

# --- Page Routing ---
if page == "File Upload and Extraction":
    from combine_texts import upload_page
    upload_page()

elif page == "View Stored Data":
    from dataview import show_view_data_page
    show_view_data_page()

