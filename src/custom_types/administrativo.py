import datetime
from typing import Annotated, Optional, List
from annotated_types import Gt
from pydantic import BaseModel

from src.helpers.dates import get_datetime_from_unix


class BaseAdministrativo(BaseModel):
    pass


class Administrativo(BaseAdministrativo):
    id: int
    nombre: str
    ci: Annotated[int, Gt(1_000_000)]
    telefono: str
    correo: str
    genero: str
    nacimiento: int
    fecha_creacion: int
    oficina: str
    usuario_id: Optional[int] = None
    medico_id: int


def AdministrativoFactory(data: List[str]):
    id, nombre, ci, telefono, correo, genero, nacimiento, fecha_creacion, oficina, medico_id = data

    return {
        "id": id,
        "nombre": nombre,
        "ci": ci,
        "telefono": telefono,
        "correo": correo,
        "genero": genero,
        "nacimiento": get_datetime_from_unix(int(nacimiento)),
        "fecha_creacion": get_datetime_from_unix(int(fecha_creacion)),
        "oficina": oficina,
        "medico_id": medico_id,
    }


def AdministrativoFactoryDates(data: List[str]):
    id, nombre, ci, telefono, correo, genero, nacimiento, fecha_creacion, oficina, medico_id = data

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
        "oficina": oficina,
        "medico_id": medico_id,
    }


class NuevoAdministrativo(BaseAdministrativo):
    oficina: str
    medico_id: int


class ActualizarAdministrativo(BaseAdministrativo):
    id: int
    nombre: str
    ci: Annotated[int, Gt(1_000_000)]
    telefono: str
    oficina: str
    usuario_id: Optional[int] = None
