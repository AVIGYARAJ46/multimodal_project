import google.generativeai as genai
import streamlit as st
import os
import pytesseract
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import speech_recognition as sr
from pydub import AudioSegment
from datetime import datetime
import tempfile
import pandas as pd
from moviepy import VideoFileClip
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound

# --- Import database functions ---
from database import init_db, store_extracted_data, fetch_all_documents_from_db

# --- Configuration ---
genai.configure(api_key="Api_key")
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# --- TEXT EXTRACTION FUNCTIONS ---

def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF."""
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def extract_text_from_docx(uploaded_file):
    """Extract text from DOCX."""
    doc = Document(uploaded_file)
    return "\n".join([para.text for para in doc.paragraphs])


def extract_text_from_image(uploaded_file):
    """Extract text from image using OCR."""
    image = Image.open(uploaded_file)
    return pytesseract.image_to_string(image)


def extract_text_from_excel(uploaded_file):
    """Extract text from Excel files."""
    try:
        xls = pd.ExcelFile(uploaded_file)
        full_text = ""
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            if not df.empty:
                full_text += f"--- Excel Sheet: {sheet_name} ---\n\n"
                full_text += df.to_string(index=False) + "\n\n"
        return full_text
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        return ""


def transcribe_audio_file(audio_path):
    """Transcribe audio from WAV file using SpeechRecognition."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio_data)
        except (sr.UnknownValueError, sr.RequestError) as e:
            st.warning(f"Audio transcription failed: {e}")
            return ""


def extract_text_from_audio(uploaded_file):
    """Extract text from audio files of various formats."""
    text = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
        try:
            temp_audio_path = f"temp_audio.{uploaded_file.name.split('.')[-1]}"
            with open(temp_audio_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            audio = AudioSegment.from_file(temp_audio_path)
            audio.export(temp_wav.name, format="wav")
            text = transcribe_audio_file(temp_wav.name)
        except Exception as e:
            st.error(f"Audio processing failed: {e}")
        finally:
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
    return text


def extract_text_from_video(uploaded_file):
    """Extract and transcribe audio from video files."""
    text = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(uploaded_file.read())
        video_path = temp_video.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
        try:
            video_clip = VideoFileClip(video_path)
            video_clip.audio.write_audiofile(temp_wav.name)
            video_clip.close()
            text = transcribe_audio_file(temp_wav.name)
        except Exception as e:
            st.error(f"Video processing failed: {e}")
        finally:
            os.remove(video_path)
    return text


# --- LLM HELPER FUNCTIONS ---

def format_context_for_llm(documents):
    """Format stored documents into a unified context for Gemini."""
    formatted_context = ""
    for doc in documents:
        formatted_context += "DOCUMENT START\n"
        formatted_context += f"FILE_NAME: {doc['file_name']}\n"
        formatted_context += f"FILE_TYPE: {doc['file_type']}\n"
        formatted_context += "CONTENT:\n"
        formatted_context += f"{doc['text']}\n"
        formatted_context += "DOCUMENT END\n\n"
    return formatted_context


def ask_gemini(context, question):
    """Ask Gemini model a question based on document context."""
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = (
        "You are a helpful Q&A assistant. Answer the user's question based *only* on the provided context below. "
        "If the answer is not found, say that clearly.\n\n"
        "--- CONTEXT ---\n"
        f"{context}\n"
        "--- QUESTION ---\n"
        f"{question}"
    )
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while contacting the AI model: {e}"


# --- MAIN STREAMLIT PAGE ---

def upload_page():
    """Main Streamlit interface for uploading and querying files."""
    st.title("🧠 Multimodal Q&A Assistant")
    st.info("Upload files (PDF, DOCX, Images, Audio, Video, Excel) or provide text to build your knowledge base.")

    # Initialize database
    init_db()

    # Fetch stored documents
    stored_documents = fetch_all_documents_from_db()

    # Store new docs in session
    if 'new_documents' not in st.session_state:
        st.session_state.new_documents = []

    # --- File Upload Section ---
    st.subheader("📂 Add from File Upload")
    uploaded_files = st.file_uploader(
        "Upload files (PDF, DOCX, Image, Audio, Video, Excel)",
        accept_multiple_files=True
    )

    if uploaded_files:
        with st.spinner("Processing uploaded files..."):
            for uploaded_file in uploaded_files:
                file_name = uploaded_file.name
                st.write(f"⏳ Processing: {file_name}")

                text = ""
                if file_name.endswith(".pdf"):
                    text = extract_text_from_pdf(uploaded_file)
                elif file_name.endswith(".docx"):
                    text = extract_text_from_docx(uploaded_file)
                elif file_name.endswith((".png", ".jpg", ".jpeg")):
                    text = extract_text_from_image(uploaded_file)
                elif file_name.endswith((".mp3", ".wav", ".flac", ".m4a")):
                    text = extract_text_from_audio(uploaded_file)
                elif file_name.endswith((".mp4", ".mov", ".avi", ".mkv")):
                    text = extract_text_from_video(uploaded_file)
                elif file_name.endswith((".xls", ".xlsx")):
                    text = extract_text_from_excel(uploaded_file)
                else:
                    st.warning(f"Unsupported file type: {file_name}")
                    continue

                if text:
                    store_extracted_data(file_name, uploaded_file.type, text)
                    st.session_state.new_documents.append({
                        "file_name": file_name,
                        "file_type": uploaded_file.type,
                        "text": text
                    })
        st.success("✅ All uploaded files have been processed and stored!")

    # Combine all documents (stored + new)
    all_documents = stored_documents + st.session_state.new_documents

    # Sidebar to show file list
    if all_documents:
        st.sidebar.subheader("📁 Files in Knowledge Base")
        displayed = set()
        for doc in all_documents:
            if doc['file_name'] not in displayed:
                st.sidebar.info(f"📄 {doc['file_name']}")
                displayed.add(doc['file_name'])

    # --- Question Section ---
    st.markdown("---")
    question = st.text_input("💬 Ask a question based on the uploaded files:")

    if st.button("Get Answer"):
        if not question:
            st.warning("Please enter a question.")
        elif not all_documents:
            st.error("❌ No files found. Please upload at least one document.")
        else:
            with st.spinner("🤔 Thinking..."):
                context = format_context_for_llm(all_documents)
                answer = ask_gemini(context=context, question=question)
                st.subheader("🧩 Answer:")
                st.write(answer)


# Run directly (for testing)
if __name__ == "__main__":
    init_db()
    upload_page()

