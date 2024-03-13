import sqlite3
from flask import Blueprint, request

from src.database.main import db_injection
from src.custom_types.usuario import ActualizarUsuario, NuevoUsuario
from src.custom_types.Api import ApiResponse, ApiResponsePayload
from src.custom_types.administrativo import ActualizarAdministrativo, AdministrativoFactory, NuevoAdministrativo
from src.errors.main import ApiErrorHandler, DbException


bp = Blueprint("administrativos", __name__, template_folder="templates")


@bp.get("/<int:administrativo_ci>")
def obtener_medico(administrativo_ci: int):
    try:
        administrativo_ci = int(administrativo_ci)

        db = db_injection()

        cursor = db.cursor()

        administrativo = cursor.execute(
            """SELECT
            usuario.id as id,
            usuario.nombre as nombre,
            usuario.ci as ci,
            usuario.telefono as telefono,
            usuario.correo as correo,
            usuario.genero as genero,
            usuario.nacimiento as nacimiento,
            usuario.fecha_creacion as fecha_creacion,
            administrativo.oficina as oficina,
            administrativo.medico_id as medico_id
            FROM usuario INNER JOIN administrativo ON usuario.id = administrativo.usuario_id WHERE ci = (?)""", (administrativo_ci,)).fetchone()

        if not administrativo:
            raise DbException(["No se encontró el médico"])

        db.close()

        return ApiResponsePayload(error=False, message=["El administrativo fue obtenido"], payload={"administrativo": AdministrativoFactory(administrativo)}).__dict__, 200
    except Exception as err:
        return ApiErrorHandler(err, "Ocurrió un error obteniendo el administrativo").__dict__, 400


@bp.post("/")
def crear_administrativo():
    try:
        usuario = NuevoUsuario(**request.get_json())
        administrativo = NuevoAdministrativo(**request.get_json())
        medico_id = administrativo.medico_id

        db = db_injection()

        cursor = db.cursor()

        medicoExists = cursor.execute(
            "SELECT id FROM medico WHERE id = ?", (medico_id,)).fetchone()
        print(medicoExists)
        if not medicoExists:
            raise DbException(["No se encontró el médico"])

        cursor.execute("INSERT INTO usuario (nombre, ci, telefono, correo, genero, nacimiento, fecha_creacion) VALUES (:nombre, :ci, :telefono, :correo, :genero, :nacimiento, :fecha_creacion)",
                       usuario.__dict__)

        usuario_id = cursor.lastrowid

        administrativo = {**administrativo.__dict__, "usuario_id": usuario_id}

        cursor.execute("INSERT INTO administrativo (oficina, usuario_id, medico_id) VALUES (:oficina, :usuario_id, :medico_id)",
                       administrativo)

        db.commit()

        return ApiResponsePayload(error=False, message=["El administrativo fue creado"], payload={"id": usuario_id, **usuario.__dict__}).__dict__, 200
    except Exception as err:
        return ApiErrorHandler(err, "Ocurrió un error creando el administrativo").__dict__, 400


@bp.put("/")
def actualizar_administrativo():
    try:
        usuario_info = ActualizarUsuario(**request.get_json())
        administrativo_info = ActualizarAdministrativo(**request.get_json())
        administrativo_id = administrativo_info.id

        db = db_injection()

        administrativo_info = request.get_json()

        cursor = db.cursor()

        cursor.execute(f"""UPDATE administrativo SET
                        oficina = :oficina
                        WHERE id = {administrativo_id}""", administrativo_info)

        cursor.execute(f"""UPDATE usuario SET
                        nombre = :nombre,
                        ci = :ci,
                        telefono = :telefono,
                        correo = :correo,
                        genero = :genero,
                        nacimiento = :nacimiento
                        WHERE id = (SELECT usuario_id FROM administrativo WHERE id = {administrativo_id})""", usuario_info.__dict__)

        db.commit()

        db.close()

        return ApiResponse(error=False, message=["El administrativo fue actualizado"]).__dict__, 200
    except Exception as err:
        print(err)
        return ApiResponse(error=True, message=["Ocurrió un error actualizando el administrativo"]).__dict__, 400


@bp.delete("/<int:administrativo_id>")
def eliminar_administrativo(administrativo_id: int):
    try:
        administrativo_id = int(administrativo_id)

        db = db_injection()

        cursor = db.cursor()

        cursor.execute(
            f"DELETE FROM usuario WHERE id = (SELECT usuario_id FROM administrativo WHERE id = (?))", (administrativo_id,))

        db.commit()

        cursor.execute(
            f"DELETE FROM administrativo WHERE id = (?)", (administrativo_id,))

        db.commit()

        db.close()

        return ApiResponse(error=False, message=["El administrativo fue eliminado"]).__dict__, 200
    except Exception as err:
        print(err)
        return ApiResponse(error=True, message=["Ocurrió un error eliminando el administrativo"]).__dict__, 400
