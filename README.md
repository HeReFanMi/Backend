# **AI Text Validator Backend**

This repository contains the backend for the AI Text Validator application, built with Python Flask. The application is containerized using Docker for easy deployment and scalability.

---

## **Project Setup**

### **1. Clone the Repository**

Clone this repository to your local machine and navigate into the project directory:

1. git clone https://github.com/HeReFanMi/Backend.git
2. cd /project

### **2. Configure Firebase database**

1. Try to creat a new firebase project, download the firebase json file which contains the configuration of your database, and add it to the root of this project.

2. in the dockerfile, don't forget to rename the json file to your firebase json file by adding the next line :

    ADD your_firebase_json_file_name.json .

### **3. Configure Environment Variables**

Create a .env file in the root directory and add your API keys and other environment-specific variables. Use the following format:

    API_KEY=your_openai_api_key
    FIREBASE_KEY=your_firebase_json_file_name.json
    DATABASE_URL=your_firebase_database_url

### **4. Build and Run the Docker Container**

1. docker build -t backend .
2. docker run --env-file .env -p 10000:10000 backend


### **5. Access the Application**

Once the container is running, access the Flask application:
Local Access: http://127.0.0.1:10000

### **6. Docker hub image**

You can find the image of this backend in the docker hub following the link of the repository below : 

    https://hub.docker.com/repository/docker/abdelaliichou/backend/general