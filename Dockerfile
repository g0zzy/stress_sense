# Dockerfile
FROM python:3.10.6-buster
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY api ./api
COPY ml_logic /ml_logic
CMD uvicorn api.fast:app --host 0.0.0.0 --port $PORT
