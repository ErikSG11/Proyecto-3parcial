# generar_clave.py
from cryptography.fernet import Fernet

# Generamos una clave y la guardamos en un archivo
key = Fernet.generate_key()
with open("secret.key", "wb") as key_file:
    key_file.write(key)

print("Clave generada y guardada en 'secret.key'")