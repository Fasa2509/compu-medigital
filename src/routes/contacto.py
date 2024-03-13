from flask import Blueprint, request
from src.custom_types.contacto_en_paciente import NuevoContactoEnPaciente

from src.database.main import db_injection
from src.custom_types.Api import ApiResponse, ApiResponsePayload
from src.custom_types.contacto import ActualizarContacto, ContactoFactory, NuevoContacto
from src.errors.main import ApiErrorHandler, DbException


bp = Blueprint("contacto", __name__, template_folder="templates")


@bp.get("/<int:ci>")
def obtener_contacto_por_ci(ci: int):
    try:
        ci = int(ci)

        db = db_injection()

        cursor = db.cursor()

        contacto_info = cursor.execute(
            """SELECT 
            id,
            nombre,
            ci,
            correo,
            relacion,
            telefono,
            genero,
            nacimiento
            FROM contacto WHERE ci = ?""", (ci,)).fetchone()

        if not contacto_info:
            raise DbException(["No se encontró el contacto"])

        db.close()

        return ApiResponsePayload(error=False, message=["El contacto fue encontrado"], payload={"contacto": ContactoFactory(contacto_info)}).__dict__, 200
    except Exception as err:
        return ApiErrorHandler(err, "Ocurrió un error buscando el contacto").__dict__, 400


@bp.post("/")
def crear_contacto():
    try:
        contacto = NuevoContacto(**request.get_json())
        paciente_id = contacto.paciente_id

        db = db_injection()

        cursor = db.cursor()

        pacienteExists = cursor.execute(
            "SELECT id FROM paciente WHERE id = ?", (paciente_id,)).fetchone()

        if not pacienteExists:
            raise DbException(["No se encontró el paciente"])

        cursor.execute("INSERT INTO contacto (nombre, ci, correo, relacion, telefono, genero, nacimiento) VALUES (:nombre, :ci, :correo, :relacion, :telefono, :genero, :nacimiento)",
                       contacto.__dict__)

        contacto_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO contacto_en_paciente (paciente_id, contacto_id) VALUES (?, ?)", (paciente_id, contacto_id))

        db.commit()

        db.close()

        return ApiResponsePayload(error=False, message=["El contacto fue creado"], payload={"id": contacto_id, **contacto.__dict__}).__dict__, 200
    except Exception as err:
        return ApiErrorHandler(err, "Ocurrió un error creando el contacto").__dict__, 400


@bp.put("/")
def actualizar_contacto():
    try:
        contacto_info = ActualizarContacto(**request.get_json())
        contacto_id = contacto_info.id

        db = db_injection()

        cursor = db.cursor()

        cursor.execute(f"""UPDATE contacto SET
                        nombre = :nombre,
                        ci = :ci,
                        correo = :correo,
                        telefono = :telefono
                        WHERE id = {contacto_id}""", contacto_info.__dict__)

        db.commit()

        db.close()

        return ApiResponse(error=False, message=["El contacto fue actualizado"]).__dict__, 200
    except Exception as err:
        print(err)
        return ApiResponse(error=True, message=["Ocurrió un error actualizando el contacto"]).__dict__, 400


@bp.patch("/")
def crear_contacto_en_paciente():
    try:
        contacto_en_paciente = NuevoContactoEnPaciente(**request.get_json())
        paciente_id = contacto_en_paciente.paciente_id
        contacto_id = contacto_en_paciente.contacto_id

        db = db_injection()

        cursor = db.cursor()

        pacienteExists = cursor.execute(
            "SELECT id FROM paciente WHERE id = ?", (paciente_id,)).fetchone()

        contactoExists = cursor.execute(
            "SELECT id FROM contacto WHERE id = ?", (contacto_id,)).fetchone()

        if not pacienteExists:
            raise DbException(["No se encontró el paciente"])

        if not contactoExists:
            raise DbException(["No se encontró el contacto"])

        connExists = cursor.execute(
            "SELECT id FROM contacto_en_paciente WHERE paciente_id = ? AND contacto_id = ?", (paciente_id, contacto_id))

        if connExists:
            db.close()
            return ApiResponsePayload(error=False, message=["El contacto ya se encuentra conectado al paciente"], payload={"id": contacto_id, **contacto_en_paciente.__dict__}).__dict__, 200

        cursor.execute("INSERT INTO contacto_en_paciente (paciente_id, contacto_id) VALUES (:paciente_id, :contacto_id)",
                       contacto_en_paciente.__dict__)

        contacto_id = cursor.lastrowid

        db.commit()

        db.close()

        return ApiResponsePayload(error=False, message=["La conexión del contacto con el paciente fue exitosa"], payload={"id": contacto_id, **contacto_en_paciente.__dict__}).__dict__, 200
    except Exception as err:
        return ApiErrorHandler(err, "Ocurrió un error conectando el contacto").__dict__, 400
