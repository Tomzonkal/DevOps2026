FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN python -c "import flask; import psycopg2; import gunicorn"

# 1. Stwórz nową grupę i użytkownika bez uprawnień 'root'
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# 2. (Opcjonalnie) nadaj mu uprawnienia do folderu z aplikacją
RUN chown -R appuser:appgroup /app

# 3. Przełącz się na tego użytkownika
USER appuser

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--preload", "app:app"]