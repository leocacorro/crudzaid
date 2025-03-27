
import os

def generar_clave(longitud=16):
    """Genera una clave aleatoria para AES."""
    if longitud not in [16, 24, 32]:
        raise ValueError("La longitud de la clave debe ser 16, 24 o 32 bytes.")
    clave = os.urandom(longitud)
    return clave

# Generar una clave de 16 bytes
clave = generar_clave(16)
print(f"Clave generada: {clave.hex()}")