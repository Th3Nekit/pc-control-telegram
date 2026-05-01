FROM python:3.11-slim

WORKDIR /app
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

CMD ["python", "main.py"]
