# **AI Text Validator Backend**

This repository contains the backend for the AI Text Validator application, built with Python Flask. The application is containerized using Docker for easy deployment and scalability.

---

## **Project Setup**

### **1. Clone the Repository**

Clone this repository to your local machine and navigate into the project directory:

```bash
git clone https://github.com/abdelaliichou/ai-text-validator-backend.git
cd ai-text-validator-backend

### **2. Configure Environment Variables**

```bash
Create a .env file in the root directory and add your API keys and other environment-specific variables. Use the following format:
API_KEY=your_openai_api_key


### **3. Build and Run the Docker Container**

```bash
docker build -t backend .
docker run --env-file .env -p 10000:10000 backend


### **4. Access the Application**

```bash
Once the container is running, access the Flask application:
Local Access: http://127.0.0.1:10000
