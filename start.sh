#!/bin/bash

# Start the Ollama server in the background
/bin/ollama serve &

# Start the Streamlit app in the foreground
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
