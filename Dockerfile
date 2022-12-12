FROM python:3.8.16-slim-buster
RUN apt-get -y update
RUN apt-get -y install git
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install protobuf==3.20
WORKDIR /app
COPY . /app
CMD ["python", "main.py"]