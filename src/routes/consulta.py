from flask import Blueprint, request

from src.database.main import db_injection
from src.custom_types.Api import ApiResponsePayload
from src.custom_types.consulta import NuevaConsulta
from src.errors.main import ApiErrorHandler, DbException


bp = Blueprint("consulta", __name__, template_folder="templates")


@bp.post("/")
def crear_consulta():
    try:
        consulta = NuevaConsulta(**request.get_json())
        medico_id = consulta.medico_id
        administrativo_id = consulta.administrativo_id
        paciente_id = consulta.paciente_id

        db = db_injection()

        cursor = db.cursor()

        medicoExists = cursor.execute(
            "SELECT id FROM medico WHERE id = ?", (medico_id,)).fetchone()

        pacienteExists = cursor.execute(
            "SELECT id FROM paciente WHERE id = ?", (paciente_id,)).fetchone()

        administrativoExists = cursor.execute(
            "SELECT id FROM administrativo WHERE id = ?", (administrativo_id,)).fetchone()

        if not medicoExists:
            raise DbException(["No se encontró el médico"])

        if not pacienteExists:
            raise DbException(["No se encontró el paciente"])

        if not administrativoExists:
            raise DbException(["No se encontró el administrativo"])

        cursor.execute("INSERT INTO consulta (fecha_consulta, fecha_creacion, coste, paciente_id, medico_id, administrativo_id) VALUES (:fecha_consulta, :fecha_creacion, :coste, :paciente_id, :medico_id, :administrativo_id)",
                       consulta.__dict__)

        consulta_id = cursor.lastrowid

        db.commit()

        db.close()

        return ApiResponsePayload(error=False, message=["La consulta fue creada"], payload={"id": consulta_id, **consulta.__dict__}).__dict__, 200
    except Exception as err:
        return ApiErrorHandler(err, "Ocurrió un error creando la consulta").__dict__, 400
