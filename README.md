## Prerequisites
Before you begin, ensure you have the following installed on your host machine (Ubuntu is recommended):

### 1. Hardware
An NVIDIA GPU (dGPU)

### 2. Software
A recent NVIDIA Driver (version 535+ recommended).

Docker Engine (version 28.4.0 or newer is recommended).

NVIDIA Container Toolkit to enable GPU access for Docker.

Docker Compose.

🚀 Getting Started
Follow these steps to build the custom Docker image and get the application running.

### 1. Clone the Repository
Clone this project to your local machine:
```bash
git clone [https://github.com/sannetyes/Deepstream_yolo_task.git](https://github.com/sannetyes/Deepstream_yolo_task.git)
cd Deepstream_yolo_task
```
### 2. Grant Display Permissions
To allow the Docker container to open a GUI window on your desktop (for the DeepStream video feed), run this command in your host terminal:

`xhost +`

### 3. Build the Docker Image
The Dockerfile in this repository automates the entire environment setup. Run the following command from the root of the project to build the image. This will take several minutes.

``` docker compose up --build -d```

`--build`: This flag tells Docker Compose to build the image from the Dockerfile before starting the services.

`-d`: This runs the container in detached (background) mode.

🏃 Running the Application
Once the image has been built, you can start, stop, and restart the application with simple commands.

To Run an Already Built Image
If you have already run the --build command once, you do not need to do it again. To start the application using the image you already built, use the following command:

docker compose up -d
