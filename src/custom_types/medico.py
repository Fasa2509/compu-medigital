from typing import Annotated
from annotated_types import Gt
from pydantic import BaseModel

from src.helpers.dates import get_datetime_from_unix


class BaseMedico(BaseModel):
    pass


class Medico(BaseMedico):
    id: int
    nombre: str
    ci: Annotated[int, Gt(1_000_000)]
    telefono: str
    correo: str
    genero: str
    nacimiento: int
    fecha_creacion: int
    especialidad: str
    usuario_id: int | None = None


def MedicoFactory(data: list[str]):
    id, nombre, ci, telefono, correo, genero, nacimiento, fecha_creacion, especialidad = data

    return {
        "id": id,
        "nombre": nombre,
        "ci": ci,
        "telefono": telefono,
        "correo": correo,
        "genero": genero,
        "nacimiento": get_datetime_from_unix(int(nacimiento)),
        "fecha_creacion": get_datetime_from_unix(int(fecha_creacion)),
        "especialidad": especialidad,
    }


class NuevoMedico(BaseMedico):
    especialidad: str


class ActualizarMedico(BaseMedico):
    id: int
    nombre: str
    ci: Annotated[int, Gt(1_000_000)]
    telefono: str
    correo: str
    genero: str
    nacimiento: int
    especialidad: str
    usuario_id: int
