FROM python:3.12-slim AS builder  
WORKDIR /install
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt
FROM python:3.12-slim
WORKDIR /training
COPY --from=builder /install /usr/local
COPY train.py .
