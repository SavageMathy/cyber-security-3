FROM python:3.11-slim-bookworm

# Crear un usuario no root
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# 1. Primero copiamos el archivo de requerimientos
COPY requirements.txt ./

# 2. Ahora instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copiamos el resto del código
COPY app.py ./
COPY templates ./templates

# Cambiar la propiedad de los archivos al usuario no root
RUN chown -R appuser:appgroup /app

# Cambiar al usuario no root
USER appuser

ENV PYTHONUNBUFFERED=1 DATABASE_PATH=/data/securedev.db
EXPOSE 8000

CMD ["python", "app.py"]