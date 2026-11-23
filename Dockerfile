FROM python:3.15-slim-bookworm
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./
COPY templates ./templates
RUN chown -R appuser:appgroup /app
USER appuser
ENV PYTHONUNBUFFERED=1 DATABASE_PATH=/data/securedev.db
EXPOSE 8000
