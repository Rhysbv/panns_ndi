FROM python:3.12.2

WORKDIR /usr/src/app

ENV FLASK_APP=app.py

ENV FLASK_RUN_HOST=0.0.0.0

COPY . .

RUN apt-get update -y && apt-get upgrade -y

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["flask", "run", "--debug"]