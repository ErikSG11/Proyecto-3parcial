# servidor.py V2 (Con Replicación)
import socket
import hashlib
from cryptography.fernet import Fernet
import os
import time

HOST = '0.0.0.0'
PORT = 5000
BUFFER_SIZE = 4096
INTERNAL_K8S_SERVICE = 'servicio-archivos' # El nombre DNS en Kubernetes

def cargar_clave():
    return open("secret.key", "rb").read()

clave = cargar_clave()
cipher = Fernet(clave)

def iniciar_servidor():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"[*] SUPER SERVIDOR V2 LISTO en {HOST}:{PORT}")

    while True:
        try:
            client_socket, addr = server_socket.accept()
            manejar_conexion(client_socket, addr)
        except Exception as e:
            print(f"Error loop: {e}")

def manejar_conexion(conn, addr):
    try:
        print(f"\n[+] Conexión entrante de {addr}")
        
        # 1. LEER LA BANDERA (1 Byte)
        tipo_mensaje = conn.recv(1).decode()
        
        if tipo_mensaje == '1':
            print("    TIPO: ORIGINAL (Viene del Cliente)")
        elif tipo_mensaje == '2':
            print("    TIPO: REPLICA (Viene de otro Pod)")
        else:
            print("    TIPO DESCONOCIDO")
            return

        # 2. Recibir Hash y Datos
        hash_recibido = conn.recv(64).decode()
        datos_encriptados = b""
        while True:
            chunk = conn.recv(BUFFER_SIZE)
            if not chunk: break
            datos_encriptados += chunk
            if len(chunk) < BUFFER_SIZE: break
        
        # 3. Validar y Guardar
        datos_desencriptados = cipher.decrypt(datos_encriptados)
        hash_calculado = hashlib.sha256(datos_desencriptados).hexdigest()
        
        if hash_recibido == hash_calculado:
            # Guardamos con nombre único
            nombre = f"archivo_{int(time.time())}_{tipo_mensaje}.txt"
            with open(nombre, "wb") as f:
                f.write(datos_desencriptados)
            
            conn.send(b"OK: Procesado")
            
            # --- LÓGICA DE REPLICACIÓN ---
            # Si es ORIGINAL ('1'), enviamos copia a los hermanos ('2')
            if tipo_mensaje == '1':
                print("    REPLICANDO A OTROS PODS...")
                replicar(hash_recibido, datos_encriptados)
        else:
            conn.send(b"ERROR: Hash incorrecto")

    except Exception as e:
        print(f"   Error: {e}")
    finally:
        conn.close()

def replicar(hash_original, datos_encriptados):
    try:
        # Conectamos al servicio interno de Kubernetes
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((INTERNAL_K8S_SERVICE, 5000))
        
        s.send(b'2') # Bandera '2' = SOY REPLICA
        s.send(hash_original.encode())
        s.send(datos_encriptados)
        s.close()
        print("    Replicación enviada.")
    except Exception as e:
        print(f"    Fallo al replicar: {e}")

if __name__ == "__main__":
    iniciar_servidor()