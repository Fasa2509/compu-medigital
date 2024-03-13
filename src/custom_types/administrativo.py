from typing import Annotated
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
    usuario_id: int | None = None
    medico_id: int


def AdministrativoFactory(data: list[str]):
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


class NuevoAdministrativo(BaseAdministrativo):
    oficina: str
    medico_id: int


class ActualizarAdministrativo(BaseAdministrativo):
    id: int
    nombre: str
    ci: Annotated[int, Gt(1_000_000)]
    telefono: str
    correo: str
    genero: str
    nacimiento: int
    oficina: str
    usuario_id: int
    medico_id: int
