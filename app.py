import streamlit as st
import os
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text, search_pdf
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *

# Float feature initialization
float_init()

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! How may I assist you today?"}
        ]

initialize_session_state()

st.title("Voice Conversational Chatbot 🤖")

# Create footer container for the microphone
footer_container = st.container()
with footer_container:
    audio_bytes = audio_recorder()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if audio_bytes:
    # Write the audio bytes to a file
    with st.spinner("Transcribing..."):
        webm_file_path = "temp_audio.mp3"
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)

        transcript = speech_to_text(webm_file_path)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            with st.chat_message("user"):
                st.write(transcript)
            os.remove(webm_file_path)

        # Check if the user's query indicates a request for a PDF search
        if "search" in transcript.lower() and "pdf" in transcript.lower():
            pdf_query = transcript.replace("search", "").replace("pdf", "").strip()
            
            # give your pdf file path
            pdf_path = "Project.pdf"
            pdf_occurrences = search_pdf(pdf_query, pdf_path)
            st.session_state.messages.append({"role": "assistant", "content": f"Occurrences in PDF: {pdf_occurrences}"})

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking🤔..."):
            final_response = get_answer(st.session_state.messages, pdf_path="Project.pdf")
        with st.spinner("Generating audio response..."):    
            audio_file = text_to_speech(final_response)
            audio_html = autoplay_audio(audio_file)
            st.markdown(audio_html, unsafe_allow_html=True)
        st.write(final_response)
        st.session_state.messages.append({"role": "assistant", "content": final_response})
        os.remove(audio_file)

# Float the footer container and provide CSS to target it with
footer_container.float("bottom: 0rem;")