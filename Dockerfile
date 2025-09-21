# Start with the official Ollama image as the foundation
FROM ollama/ollama

# Install Python, Pip, and Git
RUN apt-get update && apt-get install -y python3 python3-pip git

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your Streamlit application files into the container's working directory
COPY ./ollama_app/app.py .

# Copy and make the startup script executable
COPY start.sh /
RUN chmod +x /start.sh

# The command to run when the container starts
CMD [ "/start.sh" ]
