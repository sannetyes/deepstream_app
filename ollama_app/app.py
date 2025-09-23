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
            # Add user's VISIBLE message to chat history
            st.session_state.messages.append({
                "role": "user", 
                "content": user_input,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })

            # --- READ THE INVISIBLE LOG FILE ---
            try:
                with open("/log/log.txt", "r") as f:
                    log_content = f.read()
                    print(log_content)
            except Exception as e:
                log_content = "" # Keep it empty if there's an error

            # --- COMBINE LOG AND USER INPUT ---
            # Create the combined input that will be sent to the model
            print("\n" + "="*50, flush=True)
            combined_input = f"--- Context from log ---\n{log_content}\n--- User Question ---\n{user_input}"
            print(f"combined_input is provided as {combined_input} \n", flush=True)
            print("="*50 + "\n", flush=True)
            # For multi-turn conversation, get previous messages
            # We will replace the last user message with our new combined one
            messages_for_api = st.session_state.messages[:-1] + [
                {
                    "role": "user",
                    "content": combined_input
                }
            ]
            
            # --- GET RESPONSE FROM OLLAMA ---
            try:
                response = ollama.chat(
                    model='llama3:latest',
                    messages=messages_for_api
                )
                bot_response = response['message']['content']
            except Exception as e:
                bot_response = f"Error communicating with Ollama: {e}"
            
            # Add assistant's VISIBLE response to chat history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": bot_response,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            st.rerun()

        if clear_button:
            st.session_state.messages = []
            st.rerun()
