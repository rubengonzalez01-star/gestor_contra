from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
import bcrypt
from flasgger import Swagger

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

# Conexión a la base de datos
def conectar(vhost, vuser, vpass, vdb):
    conn = pymysql.connect(host=vhost, user=vuser, passwd=vpass, db=vdb, charset='utf8mb4')
    return conn


def serializar_registro(row):
    return {
        'id_baul': row[0],
        'Plataforma': row[1],
        'usuario': row[2],
        'clave': row[3],
    }


@app.route("/", methods=['GET'])
def api_info():
    return jsonify({'mensaje': 'API del gestor de contraseñas'})


@app.route("/baul", methods=['GET'])
def consulta_general():
    try:
        conn = conectar('localhost', 'root', '', 'gestor_contrasena')
        cur = conn.cursor()
        cur.execute("SELECT * FROM baul")
        datos = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify([serializar_registro(row) for row in datos])
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'}), 500


@app.route("/baul/<int:codigo>", methods=['GET'])
def consulta_individual(codigo):
    try:
        conn = conectar('localhost', 'root', '', 'gestor_contrasena')
        cur = conn.cursor()
        cur.execute("SELECT * FROM baul WHERE id_baul = %s", (codigo,))
        datos = cur.fetchone()
        cur.close()
        conn.close()
        if datos:
            return jsonify(serializar_registro(datos))
        return jsonify({'mensaje': 'Registro no encontrado'}), 404
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'}), 500


@app.route("/baul", methods=['POST'])
def registro():
    try:
        data = request.get_json(force=True) or {}
        plataforma = data.get('plataforma') or data.get('Plataforma')
        usuario = data.get('usuario')
        clave = data.get('clave')

        if not plataforma or not usuario or not clave:
            return jsonify({'mensaje': 'Faltan datos'}), 400

        clave_encriptada = bcrypt.hashpw(clave.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = conectar('localhost', 'root', '', 'gestor_contrasena')
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO baul (plataforma, usuario, clave) VALUES (%s, %s, %s)",
            (plataforma, usuario, clave_encriptada),
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'mensaje': 'Registro agregado'})
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'}), 500


@app.route("/baul/<int:codigo>", methods=['DELETE'])
def eliminar(codigo):
    try:
        conn = conectar('localhost', 'root', '', 'gestor_contrasena')
        cur = conn.cursor()
        cur.execute("DELETE FROM baul WHERE id_baul = %s", (codigo,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'mensaje': 'Eliminado'})
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'}), 500


@app.route("/baul/<int:codigo>", methods=['PUT'])
def actualizar(codigo):
    try:
        data = request.get_json(force=True) or {}
        plataforma = data.get('plataforma') or data.get('Plataforma')
        usuario = data.get('usuario')
        clave = data.get('clave')

        if not plataforma or not usuario or not clave:
            return jsonify({'mensaje': 'Faltan datos'}), 400

        clave_encriptada = bcrypt.hashpw(clave.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = conectar('localhost', 'root', '', 'gestor_contrasena')
        cur = conn.cursor()
        cur.execute(
            "UPDATE baul SET plataforma = %s, usuario = %s, clave = %s WHERE id_baul = %s",
            (plataforma, usuario, clave_encriptada, codigo),
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'mensaje': 'Registro actualizado'})
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'}), 500


# Compatibilidad con rutas antiguas
@app.route("/consulta_general", methods=['GET'])
def consulta_general_compat():
    return consulta_general()


@app.route("/consulta_individual/<codigo>", methods=['GET'])
def consulta_individual_compat(codigo):
    return consulta_individual(int(codigo))


@app.route("/registro/", methods=['POST'])
def registro_compat():
    return registro()


@app.route("/eliminar/<codigo>", methods=['DELETE'])
def eliminar_compat(codigo):
    return eliminar(int(codigo))


@app.route("/actualizar/<codigo>", methods=['PUT'])
def actualizar_compat(codigo):
    return actualizar(int(codigo))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)