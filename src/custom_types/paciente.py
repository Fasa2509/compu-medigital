import datetime
from typing import Annotated, Literal, Optional
from annotated_types import Gt
from pydantic import BaseModel

from src.helpers.dates import get_datetime_from_unix


class BasePaciente(BaseModel):
    pass


class Paciente(BasePaciente):
    id: int
    nombre: str
    ci: Annotated[int, Gt(1_000_000)]
    telefono: str
    correo: str
    genero: str
    nacimiento: int
    fecha_creacion: int
    direccion: str
    religion: str
    sangre: Literal["A", "B", "AB", "O"]
    usuario_id: Optional[int] = None


def PacienteFactory(data: list[str]):
    id, nombre, ci, telefono, correo, genero, nacimiento, fecha_creacion, direccion, religion, sangre = data

    return {
        "id": id,
        "nombre": nombre,
        "ci": ci,
        "telefono": telefono,
        "correo": correo,
        "genero": genero,
        "nacimiento": get_datetime_from_unix(int(nacimiento)),
        "fecha_creacion": get_datetime_from_unix(int(fecha_creacion)),
        "direccion": direccion,
        "religion": religion,
        "sangre": sangre,
    }


def PacienteFactoryDates(data: list[str]):
    id, nombre, ci, telefono, correo, genero, nacimiento, fecha_creacion, direccion, religion, sangre = data

    date = get_datetime_from_unix(int(nacimiento))

    now = datetime.datetime.now()

    less = 1 if int(date.month) > int(now.month) or int(
        date.day) > int(now.day) else 0

    years = now.year - date.year - less

    return {
        "id": id,
        "nombre": nombre,
        "ci": ci,
        "telefono": telefono,
        "correo": correo,
        "genero": genero,
        "nacimiento": f"{date.date()}, {years} años",
        "fecha_creacion": get_datetime_from_unix(int(fecha_creacion)).date().strftime("%d/%m/%Y"),
        "direccion": direccion,
        "religion": religion,
        "sangre": sangre,
    }


class NuevoPaciente(BasePaciente):
    direccion: str
    religion: str
    sangre: Literal["A", "B", "AB", "O"]


class ActualizarPaciente(BasePaciente):
    id: int
    nombre: str
    ci: Annotated[int, Gt(1_000_000)]
    telefono: str
    direccion: str
    religion: str
    sangre: Literal["A", "B", "AB", "O"]
    usuario_id: Optional[int] = None
