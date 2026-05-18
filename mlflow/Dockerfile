FROM python:3.12-slim
RUN pip install --no-cache-dir mlflow psycopg2-binary
RUN pip install --default-timeout=1000  boto3
WORKDIR /mlflow