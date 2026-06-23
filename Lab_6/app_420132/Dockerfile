FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt
COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]