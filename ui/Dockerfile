FROM continuumio/miniconda3:4.11.0
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
WORKDIR /ui
COPY . /ui
CMD ["python", "app.py"]