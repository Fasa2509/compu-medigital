import datetime
from typing import Optional, Union, Dict, List
from pydantic import BaseModel, field_validator

from src.helpers.dates import get_datetime_from_unix, get_unix_now


class BaseConsulta(BaseModel):
    pass


class Consulta(BaseConsulta):
    id: int
    fecha_consulta: int
    fecha_creacion: int
    coste: float
    paciente_id: int
    medico_id: int
    administrativo_id: int


def ConsultaFactory(data: List[str]):
    id, fecha_consulta, fecha_creacion, coste, paciente_id, medico_id, administrativo_id = data

    return {
        "id": id,
        "fecha_consulta": get_datetime_from_unix(int(fecha_consulta)),
        "fecha_creacion": get_datetime_from_unix(int(fecha_creacion)),
        "coste": coste,
        "paciente_id": paciente_id,
        "medico_id": medico_id,
        "administrativo_id": administrativo_id,
    }


def ConsultaFactoryDates(data: List[str]):
    id, fecha_consulta, fecha_creacion, coste, paciente_id, medico_id, administrativo_id = data

    return {
        "id": id,
        "fecha_consulta": get_datetime_from_unix(int(fecha_consulta)).strftime("%d/%m/%Y, %H:%M:%S"),
        "fecha_creacion": get_datetime_from_unix(int(fecha_creacion)).strftime("%d/%m/%Y"),
        "coste": coste,
        "paciente_id": paciente_id,
        "medico_id": medico_id,
        "administrativo_id": administrativo_id,
    }


def ConsultaFactoryInt(data: List[str]):
    id, fecha_consulta, fecha_creacion, coste, paciente_id, medico_id, administrativo_id = data

    return Consulta(
        id=int(id),
        fecha_consulta=int(fecha_consulta),
        fecha_creacion=int(fecha_creacion),
        coste=float(coste),
        paciente_id=int(paciente_id),
        medico_id=int(medico_id),
        administrativo_id=int(administrativo_id),
    )


class NuevaConsulta(BaseConsulta):
    fecha_consulta: int
    fecha_creacion: Optional[int] = get_unix_now()
    coste: float
    paciente_id: int
    medico_id: int
    administrativo_id: int

    @field_validator("fecha_consulta")
    @classmethod
    def revisar_fecha_consulta(cls, val: int):
        if val < get_unix_now():
            raise ValueError("La fecha no es válida")
        return val
