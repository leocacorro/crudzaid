from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
import logging  # Importar logging para manejar los logs
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import os

app = Flask(__name__)
CORS(app)

# Clave de cifrado (debe ser de 16, 24 o 32 bytes)
KEY = b'f1b416ffebb9c9e95f64a1f51c771b31' 

from Crypto.Util.Padding import pad
def cifrar_contraseña(contraseña):
    cipher = AES.new(KEY, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(contraseña.encode(), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return iv, ct

def descifrar_contraseña(iv, ct):
    try:
        iv = base64.b64decode(iv)
        ct = base64.b64decode(ct)
        cipher = AES.new(KEY, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode('utf-8')
    except (ValueError, KeyError) as e:
        print("Error al descifrar:", e)
        return None

# Conexión a la base de datos
def conectar():  # Establece la conexión a la base de datos MySQL
    conn = pymysql.connect(host='localhost', user='root', passwd='', db='sistema', charset='utf8mb4')
    return conn

# Consultar todos
@app.route("/")
def consulta_general():  # Obtiene todos los registros del baúl
    try:
        conn = conectar()
        if conn is None:
            return jsonify({'mensaje': 'Revise la conexion'})
        cur = conn.cursor()
        cur.execute("SELECT * FROM baul")
        datos = cur.fetchall()
        print(f"📄 Datos obtenidos: {datos}")  # Muestra en consola los datos obtenidos
        data = []
        for row in datos:
            # Desencriptar la contraseña antes de mostrarla
            clave = descifrar_contraseña(row[3], row[2])  # row[3] es el IV, row[2] es la clave cifrada
            dato = {'id_baul': row[0], 'Plataforma': row[1], 'usuario': row[2], 'clave': clave}
            data.append(dato)
        cur.close()
        conn.close()
        return jsonify({'baul': data, 'mensaje': 'Baúl de contraseñas'})
    except Exception as ex:
        print(" Error en consulta_general:", ex)
        return jsonify({'mensaje': 'Error en consulta_general'})

# Consultar uno
@app.route("/consulta_individual/<codigo>", methods=['GET'])
def consulta_individual(codigo):  # Obtiene un registro específico por su ID
    try:
        conn = conectar()
        if conn is None:
            return jsonify({'mensaje': 'Error de conexión'})
        cur = conn.cursor()
        cur.execute("SELECT * FROM baul WHERE id_baul=%s", (codigo,))
        datos = cur.fetchone()
        cur.close()
        conn.close()
        if datos:
            # Desencriptar la contraseña antes de mostrarla
            clave = descifrar_contraseña(datos[3], datos[2])  # datos[3] es el IV, datos[2] es la clave cifrada
            dato = {'id_baul': datos[0], 'Plataforma': datos[1], 'usuario': datos[2], 'clave': clave}
            return jsonify({'baul': dato, 'mensaje': 'Registro encontrado'})
        else:
            return jsonify({'mensaje': 'Registro no encontrado'})
    except Exception as ex:
        print(" Error en consulta_individual:", ex)
        return jsonify({'mensaje': 'Error en consulta_individual'})

# Registrar
@app.route("/registro/", methods=['POST'])
def registrar():  # Registra un nuevo usuario en la base de datos
    logging.info("Iniciando registro de usuario")  # Log para indicar que se inicia el registro
    try:
        conn = conectar()
        if conn is None:
            return jsonify({'mensaje': 'Error de conexión'})
        cur = conn.cursor()
        plataforma = request.json['plataforma']
        usuario = request.json['usuario']
        clave_plana = request.json['clave']
        
        # Cifrar la contraseña antes de almacenarla
        iv, clave_cifrada = cifrar_contraseña(clave_plana)
        cur.execute("INSERT INTO baul (plataforma, usuario, clave, iv) VALUES (%s, %s, %s, %s)", 
                    (plataforma, usuario, clave_cifrada, iv))
        conn.commit()
        cur.close()
        conn.close()
        print(f" Agregado con exito: {plataforma}, {usuario}")
        return jsonify({'mensaje': 'Registro agregado'})
    except Exception as e:
        logging.error(" Error en registrar: %s", e)
        return jsonify({'mensaje': 'Error en registrar'})

# Eliminar
@app.route("/eliminar/<codigo>", methods=['DELETE'])
def eliminar(codigo):  # Elimina un registro específico por su ID
    try:
        conn = conectar()
        if conn is None:
            return jsonify({'mensaje': 'Error de conexión'})
        cur = conn.cursor()
        cur.execute("DELETE FROM baul WHERE id_baul=%s", (codigo,))
        conn.commit()
        cur.close()
        conn.close()
        logging.info(f"🗑️ Registro eliminado: {codigo}")
        return jsonify({'mensaje': 'Eliminado'})
    except Exception as ex:
        logging.error("Error en eliminar: %s", ex)
        return jsonify({'mensaje': 'Error en eliminar'})

# Actualizar
@app.route("/actualizar/<codigo>", methods=['PUT'])
def actualizar(codigo):  # Actualiza un registro existente en la base de datos
    logging.info("Iniciando actualización del registro con id: %s", codigo)  # Log para indicar que se inicia la actualización
    try:
        conn = conectar()
        if conn is None:
            return jsonify({'mensaje': 'Error de conexión'})
        cur = conn.cursor()
        plataforma = request.json['plataforma']
        usuario = request.json['usuario']
        clave_plana = request.json['clave']
        
        # Cifrar la contraseña antes de actualizarla
        iv, clave_cifrada = cifrar_contraseña(clave_plana)
        cur.execute("UPDATE baul SET plataforma=%s, usuario=%s, clave=%s, iv=%s WHERE id_baul=%s",
                    (plataforma, usuario, clave_cifrada, iv, codigo))
        conn.commit()
        cur.close()
        conn.close()
        logging.info(f"Registro actualizado id {codigo}")
        return jsonify({'mensaje': 'Registro Actualizado'})
    except Exception as ex:
        logging.error(" Error en actualizar: %s", ex)
        return jsonify({'mensaje': 'Error en actualizar'})

# Iniciar la aplicación
if __name__ == "__main__":
    app.run(debug=True)