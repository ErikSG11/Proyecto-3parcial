# 1. Usar una imagen base de Python ligera
FROM python:3.9-slim

# --- AGREGA ESTA LÍNEA EXACTAMENTE AQUÍ ---
ENV PYTHONUNBUFFERED=1
# ------------------------------------------

# 2. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiar los archivos necesarios al contenedor
COPY requirements.txt .
COPY servidor.py .
COPY secret.key .

# 4. Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# 5. Exponer el puerto
EXPOSE 5000

# 6. Comando para iniciar
CMD ["python", "servidor.py"]