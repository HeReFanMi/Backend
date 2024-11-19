# **AI Text Validator Backend**

This repository contains the backend for the AI Text Validator application, built with Python Flask. The application is containerized using Docker for easy deployment and scalability.

---

## **Project Setup**

### **1. Clone the Repository**

Clone this repository to your local machine and navigate into the project directory:

1. git clone https://github.com/HeReFanMi/Backend.git
2. cd /project

### **2. Configure Environment Variables**

Create a .env file in the root directory and add your API keys and other environment-specific variables. Use the following format:

    API_KEY=your_openai_api_key
    FIREBASE_KEY=
    DATABASE_URL=

### **3. Build and Run the Docker Container**

1. docker build -t backend .
2. docker run --env-file .env -p 10000:10000 backend


### **4. Access the Application**

Once the container is running, access the Flask application:
Local Access: http://127.0.0.1:10000
