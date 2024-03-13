from flask import Blueprint, jsonify, request
from src.helpers.dates import get_then_unix, get_unix_now

from src.database.main import db_injection
from src.custom_types.Api import ApiResponse
from src.errors.main import ApiErrorHandler


bp = Blueprint("usuarios", __name__, template_folder="templates")


@bp.post("/")
def crear_usuario():
    try:
        db = db_injection()

        cursor = db.cursor()

        cursor.execute("INSERT INTO usuario (nombre, telefono, correo, genero, nacimiento, fecha_creacion) VALUES (?, ?, ?, ?, ?, ?)", ((
            "Miguel ejemplo", "04125790656", "mf@gmail.com", "M", get_then_unix(2001, 9, 25), get_unix_now())))

        db.commit()

        return ApiResponse(error=False, message=["si pasamos brodeeerrr"]).__dict__, 200
    except Exception as err:
        return ApiErrorHandler(err, "Ocurrió un error creando el usuario").__dict__, 400


@bp.put("/<int:usuario_id>")
def actualizar_usuario(usuario_id: int):
    try:
        usuario_id = int(usuario_id)

        db = db_injection()

        usuario_info = request.get_json()

        cursor = db.cursor()

        cursor.execute(
            f"""UPDATE usuario SET telefono = "{usuario_info.get("telefono")}", genero = "{usuario_info.get('genero')}" WHERE id = {usuario_id}""")

        db.commit()

        return ApiResponse(error=False, message=["El usuario fue actualizado"]).__dict__, 200
    except Exception as err:
        print(err)
        return ApiResponse(error=True, message=["Ocurrió un error actualizando el usuario"]).__dict__, 400


@bp.delete("/<int:usuario_id>")
def eliminar_usuario(usuario_id: int):
    try:
        usuario_id = int(usuario_id)

        db = db_injection()

        cursor = db.cursor()

        cursor.execute(f"DELETE FROM usuario WHERE id = (?)", (usuario_id,))

        db.commit()

        return ApiResponse(error=False, message=["El usuario fue eliminado"]).__dict__, 200
    except Exception as err:
        print(err)
        return ApiResponse(error=True, message=["Ocurrió un error eliminando el usuario"]).__dict__, 400
