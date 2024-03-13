from flask import Blueprint, request

from src.database.main import db_injection
from src.custom_types.Api import ApiResponsePayload
from src.custom_types.tratamiento import NuevoTratamiento
from src.errors.main import ApiErrorHandler, DbException


bp = Blueprint("tratamiento", __name__, template_folder="templates")


@bp.post("/")
def crear_tratamiento():
    try:
        tratamiento = NuevoTratamiento(**request.get_json())
        diagnostico_id = tratamiento.diagnostico_id

        db = db_injection()

        cursor = db.cursor()

        diagnosticoExists = cursor.execute(
            "SELECT id FROM diagnostico WHERE id = ?", (diagnostico_id,)).fetchone()

        if not diagnosticoExists:
            raise DbException(["No se encontró el diagnóstico"])

        cursor.execute("INSERT INTO tratamiento (indicaciones, duracion, diagnostico_id) VALUES (:indicaciones, :duracion, :diagnostico_id)",
                       tratamiento.__dict__)

        diagnostico_id = cursor.lastrowid

        db.commit()

        db.close()

        return ApiResponsePayload(error=False, message=["El diágnostico fue creado"], payload={"id": diagnostico_id, **tratamiento.__dict__}).__dict__, 200
    except Exception as err:
        return ApiErrorHandler(err, "Ocurrió un error creando el tratamiento").__dict__, 400
