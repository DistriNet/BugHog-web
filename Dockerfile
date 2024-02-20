FROM python:3.12-slim-bullseye AS web
WORKDIR /app

RUN apt update -y && apt install -y \
    build-essential \
    curl \
    libffi-dev \
    libssl-dev \
    nginx \
    supervisor \
    vim \
 && rm -rf /var/lib/apt/lists/*

COPY flask/requirements.txt .
RUN pip3 install -r requirements.txt

COPY uwsgi/website.ini .
COPY nginx/website /etc/nginx/sites-enabled/default
COPY ssl ssl
COPY flask .
COPY supervisor.conf /etc/supervisor/conf.d/supervisord.conf

CMD mkdir -p /var/log/uwsgi && \
    service supervisor start
