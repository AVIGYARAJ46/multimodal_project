import sqlite3
import streamlit as st

from database import fetch_data_from_db, delete_row_from_db

# Streamlit Interface to display data
def show_view_data_page():
    st.title("📊 View Stored Data from Database")

    # Fetch data from DB
    data = fetch_data_from_db()

    if data:
        # Create a header for your table
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 4, 1])
        with col1:
            st.subheader("File Name")
        with col2:
            st.subheader("File Type")
        with col3:
            st.subheader("Upload Time")
        with col4:
            st.subheader("Text Preview")
        with col5:
            st.subheader("Action")
        
        st.markdown("---") # Add a separator

        # Display the data for each row
        for row in data:
            row_id, file_name, file_type, extracted_text, upload_time = row

            # Layout using columns
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 4, 1])

            with col1:
                st.write(file_name)
            with col2:
                st.write(file_type)
            with col3:
                st.write(upload_time)
            with col4:
                # Display a preview of extracted text
                preview_text = (extracted_text[:100] + "...") if len(extracted_text) > 100 else extracted_text
                st.write(preview_text)
                # Expander to view full text without cluttering the UI
                with st.expander("View Full Text"):
                    st.write(extracted_text)
            with col5:
                # Use the row_id in the key to ensure it's unique
                if st.button("Delete", key=f"delete_{row_id}"):
                    delete_row_from_db(row_id)
                    st.success(f"✅ Deleted '{file_name}' successfully.")
                    # Immediately rerun the script to refresh the data display
                    st.rerun()
    else:
        st.info("ℹ️ No data found in the database.")