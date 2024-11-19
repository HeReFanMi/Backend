# download the image of python
FROM python:3.11.6-alpine

# adding the main file we are working with to this directory "."
ADD index.py .
ADD first-firebase-7e1ee-firebase-adminsdk-qbinv-48afa71695.json .

# installing all the dependecies we need to run the main file
RUN pip install flask
RUN pip install openai
RUN pip install requests
RUN pip install flask_cors
RUN pip install firebase_admin
RUN pip install python-dotenv

# instead of doing all the pip installs in the image, we can add all the
# dependecies that we need in requirements.txt file, and then we tape the 
# command => RUN pip install -r requirements.txt

# Expose the port Flask runs on
EXPOSE 10000

# the main command to run the main index.py file
CMD ["python", "./index.py"]

# to build and run this dockerfile 
# docker build -t backend .
# docker run --env-file .env -p 10000:10000 backend 
# the env file should contain API_KEY=$$$

