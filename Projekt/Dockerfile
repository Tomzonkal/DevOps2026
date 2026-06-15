FROM python:3.12-slim

WORKDIR /app

COPY app ./app

ARG APP_VERSION=local
ENV APP_VERSION=${APP_VERSION}
ENV PORT=8080
EXPOSE 8080

CMD ["python", "-m", "app.server"]
