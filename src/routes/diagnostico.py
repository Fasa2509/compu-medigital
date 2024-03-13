from flask import Blueprint, request

from src.database.main import db_injection
from src.custom_types.Api import ApiResponsePayload
from src.custom_types.diagnostico import NuevoDiagnostico
from src.errors.main import ApiErrorHandler, DbException


bp = Blueprint("diagnostico", __name__, template_folder="templates")


@bp.post("/")
def crear_diagnostico():
    try:
        diagnostico = NuevoDiagnostico(**request.get_json())
        consulta_id = diagnostico.consulta_id
        paciente_id = diagnostico.paciente_id

        db = db_injection()

        cursor = db.cursor()

        consultaExists = cursor.execute(
            "SELECT id FROM consulta WHERE id = ?", (consulta_id,)).fetchone()

        pacienteExists = cursor.execute(
            "SELECT id FROM paciente WHERE id = ?", (paciente_id,)).fetchone()

        if not consultaExists:
            raise DbException(["No se encontró la consulta"])

        if not pacienteExists:
            raise DbException(["No se encontró el paciente"])

        cursor.execute("INSERT INTO diagnostico (afectacion, observaciones, consulta_id, paciente_id, fecha_creacion) VALUES (:afectacion, :observaciones, :consulta_id, :paciente_id, :fecha_creacion)",
                       diagnostico.__dict__)

        diagnostico_id = cursor.lastrowid

        db.commit()

        db.close()

        return ApiResponsePayload(error=False, message=["El diágnostico fue creado"], payload={"id": diagnostico_id, **diagnostico.__dict__}).__dict__, 200
    except Exception as err:
        return ApiErrorHandler(err, "Ocurrió un error creando el diagnostico").__dict__, 400
