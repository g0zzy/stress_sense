FROM python:3.10.6-buster

COPY stress_sense /stress_sense
COPY requirements.txt /requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD uvicorn stress_sense.api.fast:app --host 0.0.0.0 --port $PORT
