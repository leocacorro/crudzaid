from cryptography.fernet import Fernet

key = Fernet.generate_key()
print("Tu clave secreta es:")
print(key.decode())

input("Presiona Enter para salir...")
