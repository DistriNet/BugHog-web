FROM debian:bullseye-slim
WORKDIR /app

RUN apt update -y && apt install -y \
    build-essential \
    curl \
    libffi-dev \
    libssl-dev \
    nginx \
    python3-dev \
    python3-pip \
    python3-setuptools \
    systemctl \
    vim \
 && rm -rf /var/lib/apt/lists/*

COPY flask/requirements.txt .
RUN pip3 install -r requirements.txt

COPY uwsgi/website.service /etc/systemd/system
COPY uwsgi/website.ini .
COPY nginx/website /etc/nginx/sites-enabled/default
COPY ssl ssl
COPY .pylintrc .
COPY flask .

CMD mkdir -p /var/log/uwsgi && \
    systemctl start website && \
    chmod 666 website.sock && \
    systemctl start nginx && \
    tail -f -n +1 /var/log/uwsgi/website.log
