import socket
import hashlib
from cryptography.fernet import Fernet
import os
import tkinter as tk
from tkinter import filedialog

# --- CONFIGURACIÓN ---
SERVER_IP = '127.0.0.1' 
SERVER_PORT = 60465 
# ---------------------

def cargar_clave():
    return open("secret.key", "rb").read()

clave = cargar_clave()
cipher = Fernet(clave)

def enviar_archivo(ruta_archivo):
    if not ruta_archivo:
        print(" No seleccionaste ningún archivo.")
        return

    nombre_archivo = os.path.basename(ruta_archivo)
    print(f"[*] Preparando envío de: {nombre_archivo}")
    
    with open(ruta_archivo, "rb") as f:
        datos_originales = f.read()
    print(f" Archivo leído: {len(datos_originales)} bytes")

    # 1. Hashear
    sha256_hash = hashlib.sha256(datos_originales).hexdigest()
    print(f" HASH GENERADO (SHA-256): {sha256_hash}")

    # 2. Encriptar
    datos_encriptados = cipher.encrypt(datos_originales)
    print(f" ENCRIPTADO: {len(datos_encriptados)} bytes") 
    print(f"   (Vista previa cifrada: {datos_encriptados[:50]}...)")
    
    # 3. Conectar y Enviar
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cliente.connect((SERVER_IP, SERVER_PORT))
        
        # Bandera '1' (ORIGINAL)
        cliente.send(b'1') 
        
        # Enviamos Hash y Datos
        cliente.send(sha256_hash.encode()) 
        cliente.send(datos_encriptados)
        
        respuesta = cliente.recv(1024)
        print(f" Servidor respondió: {respuesta.decode()}")
        
    except Exception as e:
        print(f" Error de conexión: {e}")
    finally:
        cliente.close()

def seleccionar_archivo():
    # Abrir ventana de selección
    root = tk.Tk()
    root.withdraw() # Ocultar la ventana principal fea
    ruta = filedialog.askopenfilename(title="Selecciona un archivo para enviar al Cluster")
    return ruta

if __name__ == "__main__":
    print("--- CLIENTE DE ALMACENAMIENTO SEGURO ---")
    archivo = seleccionar_archivo()
    enviar_archivo(archivo)