# 1. Imagen base ligera de Python
FROM python:3.14-slim

# 2. Carpeta de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiar primero las dependencias (aprovecha la caché de Docker)
COPY requirements.txt .

# 4. Instalar dependencias sin guardar caché
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar el código
COPY app.py .

# 6. Puerto que usa Flask dentro del contenedor
EXPOSE 5000

# 7. Comando de arranque
CMD ["python", "app.py"]
