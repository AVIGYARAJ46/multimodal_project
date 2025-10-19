import sqlite3
from datetime import datetime

DB_NAME = "extracted_data.db"

# --- Initialize the Database ---
def init_db():
    """Creates the database and table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS extracted_text (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            file_type TEXT,
            extracted_text TEXT,
            upload_time TEXT
        )
    ''')
    conn.commit()
    conn.close()


# --- Store Extracted Data ---
def store_extracted_data(file_name, file_type, extracted_text):
    """Inserts new extracted text data into the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO extracted_text (file_name, file_type, extracted_text, upload_time)
        VALUES (?, ?, ?, ?)
    ''', (file_name, file_type, extracted_text, upload_time))
    conn.commit()
    conn.close()


# --- Fetch All Data (for AI context or display) ---
def fetch_all_documents_from_db():
    """Fetch all records as a list of dictionaries."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT file_name, file_type, extracted_text FROM extracted_text')
    rows = cursor.fetchall()
    conn.close()

    documents = []
    if rows:
        for row in rows:
            documents.append({
                "file_name": row[0],
                "file_type": row[1],
                "text": row[2]
            })
    return documents


# --- Fetch All Data (for display in dataview.py) ---
def fetch_data_from_db():
    """Fetch all rows for viewing and deletion in dataview.py."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM extracted_text')
    rows = cursor.fetchall()
    conn.close()
    return rows


# --- Delete a Row ---
def delete_row_from_db(row_id):
    """Deletes a specific record by ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM extracted_text WHERE id = ?', (row_id,))
    conn.commit()
    conn.close()
