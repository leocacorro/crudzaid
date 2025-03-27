from flask import Flask, jsonify, request  # Importando módulos necesarios de Flask
from flask_cors import CORS  # Importando CORS para manejar el intercambio de recursos de origen cruzado
import pymysql  # Importando pymysql para conectarse a la base de datos MySQL
import logging  # Importando logging para manejar los logs
from Crypto.Cipher import AES  # Importando AES para cifrado
from Crypto.Util.Padding import pad, unpad  # Importando utilidades de padding para cifrado
import base64  # Importando base64 para codificación y decodificación
import os  # Importando os para funcionalidades del sistema operativo

app = Flask(__name__)  # Creando una instancia de la aplicación Flask
CORS(app)  # Habilitando CORS para la aplicación

# Clave de cifrado
KEY = b'f1b416ffebb9c9e95f64a1f51c771b31'  # Una clave predefinida para el cifrado AES

def cifrar_contraseña(contraseña):
    """Cifra la contraseña usando cifrado AES."""
    cipher = AES.new(KEY, AES.MODE_CBC)  # Creando un nuevo objeto de cifrado AES en modo CBC
    ct_bytes = cipher.encrypt(pad(contraseña.encode(), AES.block_size))  # Cifrando la contraseña
    iv = base64.b64encode(cipher.iv).decode('utf-8')  # Codificando el vector de inicialización (IV) en base64
    ct = base64.b64encode(ct_bytes).decode('utf-8')  # Codificando el texto cifrado en base64
    return iv, ct  # Retornando el IV y el texto cifrado

def descifrar_contraseña(iv, ct):
    """Descifra la contraseña usando cifrado AES."""
    try:
        iv = base64.b64decode(iv)  # Decodificando el IV desde base64
        ct = base64.b64decode(ct)  # Decodificando el texto cifrado desde base64
        cipher = AES.new(KEY, AES.MODE_CBC, iv)  # Creando un nuevo objeto de cifrado AES con el IV
        pt = unpad(cipher.decrypt(ct), AES.block_size)  # Desencriptando y eliminando el padding del texto plano
        return pt.decode('utf-8')  # Retornando la contraseña desencriptada
    except (ValueError, KeyError) as e:
        print("Error al descifrar:", e)  # Imprimiendo mensaje de error si falla la desencriptación
        return None  # Retornando None si falla la desencriptación

def conectar():
    """Establece una conexión a la base de datos MySQL."""
    conn = pymysql.connect(host='localhost', user='root', passwd='', db='sistema', charset='utf8mb4')  # Conectándose a la base de datos
    return conn  # Retornando el objeto de conexión

@app.route("/")  # Definiendo la ruta para la URL raíz
def consulta_general():
    """Obtiene todos los registros de la base de datos."""
    try:
        conn = conectar()  # Estableciendo conexión a la base de datos
        if conn is None:
            return jsonify({'mensaje': 'Revise la conexión'})  # Retornando mensaje de error si falla la conexión
        cur = conn.cursor()  # Creando un objeto cursor para ejecutar consultas SQL
        cur.execute("SELECT * FROM baul")  # Ejecutando consulta SQL para obtener todos los registros
        datos = cur.fetchall()  # Obteniendo todos los resultados
        print(f"📄 Datos obtenidos: {datos}")  # Imprimiendo los datos obtenidos en la consola
        data = []  # Inicializando una lista para almacenar los datos formateados
        for row in datos:
            # Desencriptar la contraseña antes de mostrarla
            clave = descifrar_contraseña(row[3], row[2])  # row[3] es el IV, row[2] es la contraseña cifrada
            dato = {'id_baul': row[0], 'Plataforma': row[1], 'usuario': row[2], 'clave': clave}
            data.append(dato)  # Agregando el registro desencriptado a la lista de datos
        cur.close()  # Cerrando el cursor
        conn.close()  # Cerrando la conexión a la base de datos
        return jsonify({'baul': data, 'mensaje': 'Baúl de contraseñas'})  # Retornando los datos en formato JSON
    except Exception as ex:
        print(" Error en consulta_general:", ex)  # Imprimiendo el error en caso de excepción
        return jsonify({'mensaje': 'Error en consulta_general'})  # Retornando mensaje de error

@app.route("/consulta_individual/<codigo>", methods=['GET'])  # Definiendo la ruta para consultar un registro específico
def consulta_individual(codigo):
    """Obtiene un registro específico por su ID."""
    try:
        conn = conectar()  # Estableciendo conexión a la base de datos
        if conn is None:
            return jsonify({'mensaje': 'Error de conexión'})  # Retornando error si la conexión falla
        cur = conn.cursor()  # Creando un cursor para ejecutar consultas
        cur.execute("SELECT * FROM baul WHERE id_baul=%s", (codigo,))  # Consultando un registro específico
        datos = cur.fetchone()  # Obteniendo un solo resultado
        cur.close()  # Cerrando el cursor
        conn.close()  # Cerrando la conexión
        if datos:
            # Desencriptar la contraseña antes de mostrarla
            clave = descifrar_contraseña(datos[3], datos[2])  # datos[3] es el IV, datos[2] es la contraseña cifrada
            dato = {'id_baul': datos[0], 'Plataforma': datos[1], 'usuario': datos[2], 'clave': clave}
            return jsonify({'baul': dato, 'mensaje': 'Registro encontrado'})  # Retornando el registro encontrado
        else:
            return jsonify({'mensaje': 'Registro no encontrado'})  # Retornando mensaje si no se encuentra el registro
    except Exception as ex:
        print(" Error en consulta_individual:", ex)  # Imprimiendo el error en caso de excepción
        return jsonify({'mensaje': 'Error en consulta_individual'})  # Retornando mensaje de error

@app.route("/registro/", methods=['POST'])  # Definiendo la ruta para registrar un nuevo usuario
def registrar():
    """Registra un nuevo usuario en la base de datos."""
    logging.info("Iniciando registro de usuario")  # Log para indicar que se inicia el registro
    try:
        conn = conectar()  # Estableciendo conexión a la base de datos
        if conn is None:
            return jsonify({'mensaje': 'Error de conexión'})  # Retornando error si la conexión falla
        cur = conn.cursor()  # Creando un cursor para ejecutar consultas
        plataforma = request.json['plataforma']  # Obteniendo la plataforma del cuerpo de la solicitud
        usuario = request.json['usuario']  # Obteniendo el usuario del cuerpo de la solicitud
        clave_plana = request.json['clave']  # Obteniendo la contraseña del cuerpo de la solicitud
        
        # Cifrar la contraseña antes de almacenarla
        iv, clave_cifrada = cifrar_contraseña(clave_plana)  # Cifrando la contraseña
        cur.execute("INSERT INTO baul (plataforma, usuario, clave, iv) VALUES (%s, %s, %s, %s)", 
                    (plataforma, usuario, clave_cifrada, iv))  # Insertando el nuevo registro en la base de datos
        conn.commit()  # Confirmando los cambios en la base de datos
        cur.close()  # Cerrando el cursor
        conn.close()  # Cerrando la conexión
        print(f" Agregado con exito: {plataforma}, {usuario}")  # Imprimiendo mensaje de éxito
        return jsonify({'mensaje': 'Registro agregado'})  # Retornando mensaje de éxito
    except Exception as e:
        logging.error(" Error en registrar: %s", e)  # Registrando el error en caso de excepción
        return jsonify({'mensaje': 'Error en registrar'})  # Retornando mensaje de error

@app.route("/eliminar/<codigo>", methods=['DELETE'])  # Definiendo la ruta para eliminar un registro específico
def eliminar(codigo):
    """Elimina un registro específico por su ID."""
    try:
        conn = conectar()  # Estableciendo conexión a la base de datos
        if conn is None:
            return jsonify({'mensaje': 'Error de conexión'})  # Retornando error si la conexión falla
        cur = conn.cursor()  # Creando un cursor para ejecutar consultas
        cur.execute("DELETE FROM baul WHERE id_baul=%s", (codigo,))  # Ejecutando la consulta para eliminar el registro
        conn.commit()  # Confirmando los cambios en la base de datos
        cur.close()  # Cerrando el cursor
        conn.close()  # Cerrando la conexión
        logging.info(f"🗑️ Registro eliminado: {codigo}")  # Registrando el éxito de la eliminación
        return jsonify({'mensaje': 'Eliminado'})  # Retornando mensaje de éxito
    except Exception as ex:
        logging.error("Error en eliminar: %s", ex)  # Registrando el error en caso de excepción
        return jsonify({'mensaje': 'Error en eliminar'})  # Retornando mensaje de error

@app.route("/actualizar/<codigo>", methods=['PUT'])  # Definiendo la ruta para actualizar un registro existente
def actualizar(codigo):
    """Actualiza un registro existente en la base de datos."""
    logging.info("Iniciando actualización del registro con id: %s", codigo)  # Log para indicar que se inicia la actualización
    try:
        conn = conectar()  # Estableciendo conexión a la base de datos
        if conn is None:
            return jsonify({'mensaje': 'Error de conexión'})  # Retornando error si la conexión falla
        cur = conn.cursor()  # Creando un cursor para ejecutar consultas
        plataforma = request.json['plataforma']  # Obteniendo la plataforma del cuerpo de la solicitud
        usuario = request.json['usuario']  # Obteniendo el usuario del cuerpo de la solicitud
        clave_plana = request.json['clave']  # Obteniendo la contraseña del cuerpo de la solicitud
        
        # Cifrar la contraseña antes de actualizarla
        iv, clave_cifrada = cifrar_contraseña(clave_plana)  # Cifrando la contraseña
        cur.execute("UPDATE baul SET plataforma=%s, usuario=%s, clave=%s, iv=%s WHERE id_baul=%s",
                    (plataforma, usuario, clave_cifrada, iv, codigo))  # Actualizando el registro en la base de datos
        conn.commit()  # Confirmando los cambios en la base de datos
        cur.close()  # Cerrando el cursor
        conn.close()  # Cerrando la conexión
        logging.info(f"Registro actualizado id {codigo}")  # Registrando el éxito de la actualización
        return jsonify({'mensaje': 'Registro Actualizado'})  # Retornando mensaje de éxito
    except Exception as ex:
        logging.error(" Error en actualizar: %s", ex)  # Registrando el error en caso de excepción
        return jsonify({'mensaje': 'Error en actualizar'})  # Retornando mensaje de error

# Iniciar la aplicación
if __name__ == "__main__":
    app.run(debug=True)  # Ejecutando la aplicación en modo de depuración
