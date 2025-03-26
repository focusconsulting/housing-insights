FROM python:3.5-slim-buster

RUN apt-get update && apt-get -y install  postgresql libpq-dev build-essential

# Set up code directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "application.py"]