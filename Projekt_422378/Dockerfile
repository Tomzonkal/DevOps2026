# Używamy lekkiego obrazu Pythona
FROM python:3.9-slim

# Tworzymy folder roboczy wewnątrz kontenera
WORKDIR /app

# Kopiujemy plik z wymaganiami i instalujemy Flaska
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy kod naszej aplikacji
COPY app.py .

# Otwieramy port 8080, na którym działa aplikacja
EXPOSE 8080

# Komenda uruchamiająca serwer
CMD ["python", "app.py"]