FROM continuumio/miniconda3:4.11.0
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt --no-cache-dir
RUN pip install protobuf==3.20
CMD ["python", "main.py"]