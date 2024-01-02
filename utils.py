from openai import OpenAI
import os
from dotenv import load_dotenv
import base64
import fitz  # PyMuPDF for PDF processing

load_dotenv()
api_key = os.getenv("openai_api_key")

client = OpenAI(api_key=api_key)
def get_answer(messages, pdf_path=None):
    system_message = [{"role": "system", "content": "You are a helpful AI chatbot that answers questions asked by the User."}]
    messages = system_message + messages

    # Extract text from PDF if a PDF path is provided
    pdf_text = ""
    if pdf_path:
        pdf_text = extract_text_from_pdf(pdf_path)

    # Include PDF text in the messages
    if pdf_text:
        messages.append({"role": "assistant", "content": pdf_text})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages
    )

    return response.choices[0].message.content

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def speech_to_text(audio_data):
    with open(audio_data, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            response_format="text",
            file=audio_file
        )
    return transcript

def text_to_speech(input_text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=input_text
    )
    webm_file_path = "temp_audio_play.mp3"
    with open(webm_file_path, "wb") as f:
        response.stream_to_file(webm_file_path)
    return webm_file_path

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    md = f"""
    <audio autoplay>
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    return md

# Function to search for a query in a PDF file
def search_pdf(query, pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text()

        return text.lower().count(query.lower())
    except Exception as e:
        print(f"Error searching PDF: {e}")
        return 0