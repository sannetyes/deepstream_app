# Start from the official NVIDIA DeepStream base image
FROM nvcr.io/nvidia/deepstream:7.1-triton-multiarch

# Set an environment variable to prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# --------------------BINDINGS---------------------------------
# 1. Install all system prerequisites in a single layer for efficiency
RUN apt-get update && apt-get install -y \
    python3-gi \
    python3-dev \
    python3-gst-1.0 \
    python-gi-dev \
    git \
    meson \
    python3 \
    python3-pip \
    python3.10-dev \
    cmake \
    g++ \
    build-essential \
    libglib2.0-dev \
    libglib2.0-dev-bin \
    libgstreamer1.0-dev \
    libtool \
    m4 \
    autoconf \
    automake \
    libgirepository1.0-dev \
    pkg-config libcairo2-dev \
    libcairo2-dev \
    pkg-config \
    # Clean up apt cache to reduce the final image size
    && rm -rf /var/lib/apt/lists/*

# 2. Install Python build dependencies
RUN pip3 install build setuptools wheel

WORKDIR /opt/nvidia/deepstream/deepstream-7.1/sources

RUN git clone https://github.com/NVIDIA-AI-IOT/deepstream_python_apps.git

WORKDIR /opt/nvidia/deepstream/deepstream-7.1/sources/deepstream_python_apps

RUN git checkout v1.2.0

# 5. Initialize the Git submodules for Python bindings
RUN git submodule update --init && \
    python3 bindings/3rdparty/git-partial-submodule/git-partial-submodule.py restore-sparse

# 6. Build and install the gst-python bindings from its subproject directory
RUN cd bindings/3rdparty/gstreamer/subprojects/gst-python/ && \
    meson setup build && \
    cd build && \
    ninja && \
    ninja install

# 7. Compile the main pyds bindings
# 8. Compile the main pyds bindings
WORKDIR /opt/nvidia/deepstream/deepstream-7.1/sources/deepstream_python_apps/bindings
RUN export CMAKE_BUILD_PARALLEL_LEVEL=$(nproc)

RUN python3 -m build

RUN cd dist/ && \
    pip3 install ./pyds-1.2.0-*.whl
