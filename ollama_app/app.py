#!/usr/bin/env python3
import streamlit as st
from datetime import datetime
from streamlit_webrtc import webrtc_streamer, RTCConfiguration, VideoTransformerBase, WebRtcMode
import ollama
import av
import cv2

# --- Configuration ---
RTSP_URL = "rtsp://deepstream:8554/ds-feed"
OLLAMA_HOST = "http://localhost:11434"
LOG_FILE_PATH = "/log/log.txt"

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Camera and Chatbot Interface")
st.title("DeepStream Vision AI Interface")

# --- Initialization of Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Custom Video Transformer for RTSP (Compatible Version) ---
class RTSPVideoTransformer(VideoTransformerBase):
    def __init__(self, rtsp_url):
        self.cap = cv2.VideoCapture(rtsp_url)
        if not self.cap.isOpened():
            print(f"Error: Could not open RTSP stream at {rtsp_url}")
        self.last_frame = None

    def transform(self, frame):
        ret, new_frame = self.cap.read()
        if not ret:
            return self.last_frame
        self.last_frame = new_frame
        return new_frame

# --- Main Application Layout ---
col1, col2 = st.columns([2, 1], gap="large")

# --- Column 1: Real-time Camera Stream ---
with col1:
    st.header("Live DeepStream Feed")
    st.markdown("This is the real-time, annotated video stream from the DeepStream service.")
    
    webrtc_streamer(
        key="deepstream-rtsp",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        ),
        media_stream_constraints={"video": True, "audio": False},
        video_transformer_factory=lambda: RTSPVideoTransformer(RTSP_URL)
    )

# --- Column 2: Chatbot Interface ---
with col2:
    st.header("Chatbot")
    st.markdown("Interact with the chatbot below.")

    # Display the entire chat history at the top
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "timestamp" in message:
                st.markdown(f"*{message['timestamp']}*")
            st.write(message["content"])

    # The chat input is the main event handler
    if user_input := st.chat_input("Your message..."):
        # 1. Add and immediately display the user's message
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        with st.chat_message("user"):
            st.markdown(f"*{datetime.now().strftime('%H:%M:%S')}*")
            st.write(user_input)

        # 2. Get and display the assistant's response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    with open(LOG_FILE_PATH, "r") as f:
                        log_content = f.read()
                except Exception as e:
                    log_content = f"Could not read log file: {e}"

                combined_input = (
                    "You are an AI assistant analyzing a real-time video metadata log. "
                    "Use the following log to answer the user's question.\n\n"
                    f"--- METADATA LOG ---\n{log_content}\n--- END OF LOG ---\n\n"
                    f"User Question: {user_input}"
                )
                
                try:
                    client = ollama.Client(host=OLLAMA_HOST)
                    stream = client.chat(
                        model='llama3',
                        messages=[{'role': 'user', 'content': combined_input}],
                        stream=True
                    )
                    bot_response = st.write_stream(
                        (chunk['message']['content'] for chunk in stream)
                    )
                except Exception as e:
                    bot_response = f"Error communicating with Ollama: {e}"
                    st.error(bot_response)

        # 3. Add the full assistant response to the session state for the next rerun
        st.session_state.messages.append({
            "role": "assistant", 
            "content": bot_response,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
