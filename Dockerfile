FROM continuumio/miniconda3:4.11.0
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt --no-cache-dir
CMD ["python", "main.py"]