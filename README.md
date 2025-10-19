# 🧠 Multimodal Data Extraction and Viewer App

This project is a **Streamlit-based web application** that allows users to **upload files, extract text data, store it in a database, and view or manage it easily**.  
It supports multimodal input (such as PDFs, text, and image-based documents), and stores extracted text in an SQLite database for later review or deletion.

---

## 🚀 Features

- 📂 **Upload Files:** Upload PDF, DOCX, TXT, or image files.
- 🧠 **Automatic Text Extraction:** Uses `PyPDF2`, `python-docx`, and `pytesseract` for OCR-based extraction.
- 💾 **Database Storage:** Extracted data is stored in a local SQLite database.
- 📊 **Data Viewer Interface:** View and delete extracted records easily through the UI.
- ⚡ **Streamlit-Powered Frontend:** Simple, interactive, and lightweight web interface.

---

## 🧩 Project Structure

Create a virtual environment
python -m venv vir

3️⃣ Activate the environment

Windows:

vir\Scripts\activate


macOS/Linux:

source vir/bin/activate

4️⃣ Install dependencies
pip install -r requirements.txt

5️⃣ Run the Streamlit app
streamlit run app.py
