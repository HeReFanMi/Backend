FROM python:3.11.6-alpine

ADD index.py .
# ADD firebase.json . // your own json file that contain your firebase informations

RUN pip install flask
RUN pip install openai
RUN pip install requests
RUN pip install flask_cors
RUN pip install firebase_admin
RUN pip install python-dotenv

EXPOSE 10000

CMD ["python", "./index.py"]

# docker build -t backend .
# docker run --env-file .env -p 10000:10000 backend 

