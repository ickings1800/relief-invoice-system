FROM python:3.6-buster
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN \
 apt-get install python3.6 && \
 apt-get install libjpeg-dev zlib1g-dev && \
 python3 -m pip install -r ./requirements/local.txt --no-cache-dir