# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

EXPOSE 8080

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install -r requirements.txt

RUN apt-get update
# RUN apt-get install tesseract-ocr -y
RUN apt-get install poppler-utils -y
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# Run the web service
CMD python manage.py runserver 0.0.0.0:8080