# Start with the official Ollama image as the foundation

FROM ollama/ollama

# Install Python, Pip, Git, and the venv module

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    python3.12-venv \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y python3 python3-pip git python3.12-venv

# Create a virtual environment
RUN python3 -m venv /opt/venv

# Activate the virtual environment for all subsequent commands
ENV PATH="/opt/venv/bin:$PATH"

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies into the venv
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your Streamlit application files
COPY . .

# Copy and make the startup script executable
COPY start.sh /
RUN chmod +x /start.sh

# Reset the entrypoint from the base image so our script can run directly
ENTRYPOINT []

# The command to run when the container starts
CMD [ "/start.sh" ]
