#!/usr/bin/env python3
import streamlit as st
from datetime import datetime
from streamlit_webrtc import webrtc_streamer
import ollama # <--- 1. IMPORT OLLAMA

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Camera and Chatbot Interface")

# --- Initialization of Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Main Application Layout ---
col1, col2 = st.columns([1, 1], gap="large")

# --- Column 1: Real-time Camera Stream ---
with col1:
    st.header("Camera Feed")
    st.markdown("This is your real-time camera stream. Allow the browser to access your camera.")
    webrtc_streamer(key="live-stream")

# --- Column 2: Chatbot Interface ---
with col2:
    st.header("Chatbot")
    st.markdown("Interact with the chatbot below.")

    # --- Chat Display Area ---
    chat_container = st.container(height=400)
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(f"*{message['timestamp']}*")
                st.write(message["content"])

    # --- Chat Input and Controls Area ---
    controls_container = st.container()
    with controls_container:
        with st.form(key='chat_form', clear_on_submit=True):
            user_input = st.text_input("Your message:", placeholder="Type your message here...", key="input_text")
            
            form_cols = st.columns([1, 1, 2])
            with form_cols[0]:
                send_button = st.form_submit_button(label="Send")
            with form_cols[1]:
                clear_button = st.form_submit_button(label="Clear")

        # --- Button Logic ---
        if send_button and user_input:
            # Add user's message to chat history
            st.session_state.messages.append({
                "role": "user", 
                "content": user_input,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })

            # --- 2. GET RESPONSE FROM OLLAMA ---
            # Replace the canned response with a call to the Ollama API
            try:
                # Use the ollama.chat function
                response = ollama.chat(
                    model='gemma3:270m', # Specify the model you want to use
                    messages=[
                        {'role': 'user', 'content': user_input}
                    ]
                )
                bot_response = response['message']['content']
            except Exception as e:
                # Handle potential connection errors
                bot_response = f"Error: Could not connect to Ollama. Is it running?\n\n{e}"
            
            # Add assistant's response to chat history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": bot_response,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            # Rerun the app to display new messages
            st.rerun()

        if clear_button:
            st.session_state.messages = []
            st.rerun()
