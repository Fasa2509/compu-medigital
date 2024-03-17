import datetime
from pydantic import BaseModel

from src.helpers.dates import get_datetime_from_unix, get_then_unix, get_unix_now


class BaseDiagnostico(BaseModel):
    pass


class Diagnostico(BaseDiagnostico):
    id: int
    afectacion: str
    observaciones: str
    fecha_creacion: int
    consulta_id: int
    paciente_id: int


def DiagnosticoFactory(data: list[str]):
    id, afectacion, observaciones, fecha_creacion, consulta_id, paciente_id = data

    return {
        "id": id,
        "afectacion": afectacion,
        "observaciones": observaciones,
        "fecha_creacion": fecha_creacion,
        "consulta_id": consulta_id,
        "paciente_id": paciente_id,
    }


def DiagnosticoFactoryDates(data: list[str]):
    id, afectacion, observaciones, fecha_creacion, consulta_id, paciente_id = data

    return {
        "id": id,
        "afectacion": afectacion,
        "observaciones": observaciones,
        "fecha_creacion": get_datetime_from_unix(int(fecha_creacion)).strftime("%d/%m%Y, %H:%M:%S"),
        "consulta_id": consulta_id,
        "paciente_id": paciente_id,
    }


class NuevoDiagnostico(BaseDiagnostico):
    afectacion: str
    observaciones: str
    consulta_id: int
    paciente_id: int
    fecha_creacion: int | None = get_unix_now()
