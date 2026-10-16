from contextlib import contextmanager

from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
import bcrypt
from flasgger import Swagger, swag_from

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)


# ---------------------------------------------------------------------------
# Conexión a la base de datos
# ---------------------------------------------------------------------------
def conectar(vhost, vuser, vpass, vdb):
    return pymysql.connect(
        host=vhost,
        user=vuser,
        password=vpass,   # antes: passwd
        database=vdb,     # antes: db
        charset='utf8mb4',
    )


@contextmanager
def obtener_cursor():
    """Una conexión por petición: commit si sale bien, rollback si falla
    y siempre close (evita el Lock wait timeout)."""
    conn = conectar('localhost', 'root', '', 'gestor_contrasena')
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def serializar_registro(row):
    return {
        'id_baul': row[0],
        'Plataforma': row[1],
        'usuario': row[2],
        'clave': row[3],
    }


def leer_datos():
    data = request.get_json(force=True, silent=True) or {}
    plataforma = data.get('plataforma') or data.get('Plataforma')
    usuario = data.get('usuario')
    clave = data.get('clave')
    return plataforma, usuario, clave


def encriptar(clave):
    return bcrypt.hashpw(clave.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


# ---------------------------------------------------------------------------
# Documentación Swagger (diccionarios, no dependen de docstrings)
# ---------------------------------------------------------------------------
PARAM_ID = {
    'name': 'codigo', 'in': 'path', 'type': 'integer',
    'required': True, 'description': 'id_baul del registro',
}

PARAM_BODY = {
    'name': 'body', 'in': 'body', 'required': True,
    'schema': {
        'type': 'object',
        'properties': {
            'plataforma': {'type': 'string', 'example': 'facebook'},
            'usuario': {'type': 'string', 'example': 'ruben'},
            'clave': {'type': 'string', 'example': 'miClave123'},
        },
    },
}

DOC_INFO = {
    'tags': ['General'],
    'summary': 'Información de la API',
    'responses': {'200': {'description': 'Mensaje de bienvenida'}},
}

DOC_LISTAR = {
    'tags': ['Baúl'],
    'summary': 'Listar todos los registros del baúl',
    'responses': {
        '200': {'description': 'Lista de registros'},
        '500': {'description': 'Error del servidor'},
    },
}

DOC_CONSULTAR = {
    'tags': ['Baúl'],
    'summary': 'Consultar un registro por id',
    'parameters': [PARAM_ID],
    'responses': {
        '200': {'description': 'Registro encontrado'},
        '404': {'description': 'Registro no encontrado'},
        '500': {'description': 'Error del servidor'},
    },
}

DOC_CREAR = {
    'tags': ['Baúl'],
    'summary': 'Agregar un registro',
    'parameters': [PARAM_BODY],
    'responses': {
        '200': {'description': 'Registro agregado'},
        '400': {'description': 'Faltan datos'},
        '500': {'description': 'Error del servidor'},
    },
}

DOC_ELIMINAR = {
    'tags': ['Baúl'],
    'summary': 'Eliminar un registro',
    'parameters': [PARAM_ID],
    'responses': {
        '200': {'description': 'Registro eliminado'},
        '500': {'description': 'Error del servidor'},
    },
}

DOC_ACTUALIZAR = {
    'tags': ['Baúl'],
    'summary': 'Actualizar un registro',
    'parameters': [PARAM_ID, PARAM_BODY],
    'responses': {
        '200': {'description': 'Registro actualizado'},
        '400': {'description': 'Faltan datos'},
        '500': {'description': 'Error del servidor'},
    },
}


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
@app.route("/", methods=['GET'])
@swag_from(DOC_INFO)
def api_info():
    return jsonify({'mensaje': 'API del gestor de contraseñas'})


@app.route("/baul", methods=['GET'])
@swag_from(DOC_LISTAR)
def consulta_general():
    try:
        with obtener_cursor() as cur:
            cur.execute("SELECT id_baul, plataforma, usuario, clave FROM baul")
            datos = cur.fetchall()
        return jsonify([serializar_registro(row) for row in datos])
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'}), 500


@app.route("/baul/<int:codigo>", methods=['GET'])
@swag_from(DOC_CONSULTAR)
def consulta_individual(codigo):
    try:
        with obtener_cursor() as cur:
            cur.execute(
                "SELECT id_baul, plataforma, usuario, clave FROM baul WHERE id_baul = %s",
                (codigo,),
            )
            datos = cur.fetchone()
        if datos:
            return jsonify(serializar_registro(datos))
        return jsonify({'mensaje': 'Registro no encontrado'}), 404
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'}), 500


@app.route("/baul", methods=['POST'])
@swag_from(DOC_CREAR)
def registro():
    try:
        plataforma, usuario, clave = leer_datos()
        if not plataforma or not usuario or not clave:
            return jsonify({'mensaje': 'Faltan datos'}), 400

        with obtener_cursor() as cur:
            cur.execute(
                "INSERT INTO baul (plataforma, usuario, clave) VALUES (%s, %s, %s)",
                (plataforma, usuario, encriptar(clave)),
            )
        return jsonify({'mensaje': 'Registro agregado'})
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'}), 500


@app.route("/baul/<int:codigo>", methods=['DELETE'])
@swag_from(DOC_ELIMINAR)
def eliminar(codigo):
    try:
        with obtener_cursor() as cur:
            cur.execute("DELETE FROM baul WHERE id_baul = %s", (codigo,))
        return jsonify({'mensaje': 'Eliminado'})
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'}), 500


@app.route("/baul/<int:codigo>", methods=['PUT'])
@swag_from(DOC_ACTUALIZAR)
def actualizar(codigo):
    try:
        plataforma, usuario, clave = leer_datos()
        if not plataforma or not usuario or not clave:
            return jsonify({'mensaje': 'Faltan datos'}), 400

        with obtener_cursor() as cur:
            cur.execute(
                "UPDATE baul SET plataforma = %s, usuario = %s, clave = %s WHERE id_baul = %s",
                (plataforma, usuario, encriptar(clave), codigo),
            )
        return jsonify({'mensaje': 'Registro actualizado'})
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'}), 500


# ---------------------------------------------------------------------------
# Compatibilidad con rutas antiguas (no aparecen en Swagger)
# ---------------------------------------------------------------------------
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
    app.run(debug=True, host='127.0.0.1', port=5000)