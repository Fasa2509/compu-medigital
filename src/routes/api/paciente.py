from flask import Blueprint, request

from src.database.main import db_injection
from src.custom_types.usuario import ActualizarUsuario, NuevoUsuario
from src.custom_types.Api import ApiResponse, ApiResponsePayload
from src.custom_types.paciente import ActualizarPaciente, NuevoPaciente, PacienteFactory
from src.errors.main import ApiErrorHandler, DbException, ValidationException


bp = Blueprint("pacientes", __name__, template_folder="templates")


@bp.get("/<int:paciente_ci>")
def obtener_paciente(paciente_ci: int):
    try:
        paciente_ci = int(paciente_ci)

        db = db_injection()

        cursor = db.cursor()

        paciente = cursor.execute(
            """SELECT
            usuario.id as id,
            usuario.nombre as nombre,
            usuario.ci as ci,
            usuario.telefono as telefono,
            usuario.correo as correo,
            usuario.genero as genero,
            usuario.nacimiento as nacimiento,
            usuario.fecha_creacion as fecha_creacion,
            paciente.direccion as direccion,
            paciente.religion as religion,
            paciente.sangre as sangre
            FROM usuario INNER JOIN paciente ON usuario.id = paciente.usuario_id WHERE ci = (?)""", (paciente_ci,)).fetchone()

        if not paciente:
            raise DbException(["No se encontró el paciente"])

        db.close()

        return ApiResponsePayload(error=False, message=["El paciente fue obtenido"], payload={"paciente": PacienteFactory(paciente)}).__dict__, 200
    except Exception as err:
        return ApiErrorHandler(err, "Ocurrió un error obteniendo el paciente").__dict__, 400


@bp.post("/")
def crear_paciente():
    try:
        usuario = NuevoUsuario(**request.get_json())
        paciente = NuevoPaciente(**request.get_json())

        if not usuario.clave or len(usuario.clave) < 8:
            raise ValueError("La contraseña no es válida")

        db = db_injection()

        cursor = db.cursor()

        cursor.execute("INSERT INTO usuario (nombre, clave, ci, telefono, correo, genero, nacimiento, fecha_creacion) VALUES (:nombre, :clave, :ci, :telefono, :correo, :genero, :nacimiento, :fecha_creacion)",
                       usuario.__dict__)

        usuario_id = cursor.lastrowid

        paciente = {**paciente.__dict__, "usuario_id": usuario_id}

        cursor.execute("INSERT INTO paciente (direccion, religion, sangre, usuario_id) VALUES (:direccion, :religion, :sangre, :usuario_id)",
                       paciente)

        db.commit()

        return ApiResponsePayload(error=False, message=["El paciente fue creado"], payload={"id": usuario_id, **usuario.__dict__}).__dict__, 200
    except Exception as err:
        return ApiErrorHandler(err, "Ocurrió un error creando el paciente").__dict__, 400


@bp.put("/")
def actualizar_paciente():
    try:
        usuario_info = ActualizarUsuario(**request.get_json())
        paciente_info = ActualizarPaciente(**request.get_json())

        paciente_id = paciente_info.id

        db = db_injection()

        cursor = db.cursor()

        cursor.execute(f"""UPDATE paciente SET
                        direccion = :direccion,
                        religion = :religion,
                        sangre = :sangre
                        WHERE id = {paciente_id}""", paciente_info.__dict__)

        cursor.execute(f"""UPDATE usuario SET
                        nombre = :nombre,
                        ci = :ci,
                        telefono = :telefono
                        WHERE id = (SELECT usuario_id FROM paciente WHERE id = {paciente_id})""", usuario_info.__dict__)

        db.commit()

        db.close()

        return ApiResponse(error=False, message=["El paciente fue actualizado"]).__dict__, 200
    except Exception as err:
        print(err)
        return ApiResponse(error=True, message=["Ocurrió un error actualizando el paciente"]).__dict__, 400


@bp.delete("/<int:paciente_id>")
def eliminar_paciente(paciente_id: int):
    try:
        paciente_id = int(paciente_id)

        db = db_injection()

        cursor = db.cursor()

        cursor.execute(
            f"DELETE FROM usuario WHERE id = (SELECT usuario_id FROM paciente WHERE id = ?)", (paciente_id,))

        db.commit()

        cursor.execute(f"DELETE FROM paciente WHERE id = (?)", (paciente_id,))

        db.commit()

        db.close()

        return ApiResponse(error=False, message=["El paciente fue eliminado"]).__dict__, 200
    except Exception as err:
        print(err)
        return ApiResponse(error=True, message=["Ocurrió un error eliminando el paciente"]).__dict__, 400
