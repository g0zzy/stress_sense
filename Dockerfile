FROM python:3.10.6-slim-buster

COPY api /api
COPY stress_sense /stress_sense
COPY models /models
COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
# RUN /bin/bash -c "python stress_sense/scripts.py"

CMD uvicorn api.fast:app --host 0.0.0.0 --port $PORT
