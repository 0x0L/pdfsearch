FROM continuumio/miniconda3

RUN apt-get update && apt-get install -y poppler-utils

RUN conda update --all

RUN pip install flask nltk

RUN python -m nltk.downloader punkt

WORKDIR /app
COPY . /app

ENV FLASK_APP=app.py
CMD flask run --host=0.0.0.0
