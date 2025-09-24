#!/bin/bash

# Start the Ollama server in the background
/bin/ollama serve &

# Wait a moment for the server to start
sleep 5

# Check if the desired model is already pulled
if ! ollama list | grep -q llama3; then
  echo "Llama3 model not found. Pulling it..."
  ollama pull llama3:latest
fi

# Start the Streamlit app in the foreground
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
