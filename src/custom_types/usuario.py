from typing import Annotated, Literal
from annotated_types import Gt
from pydantic import BaseModel, field_validator

from src.helpers.dates import get_unix_now


class BaseUsuario(BaseModel):
    pass


class Usuario(BaseUsuario):
    id: str | int
    nombre: str
    ci: Annotated[int, Gt(1_000_000)]
    telefono: str
    correo: str
    genero: str
    nacimiento: int
    fecha_creacion: int

    @field_validator("id", mode="before")
    @classmethod
    def transform_id(cls, val: str) -> int:
        return int(val)


class NuevoUsuario(BaseUsuario):
    nombre: str
    ci: Annotated[int, Gt(1_000_000)]
    telefono: str
    correo: str
    genero: Literal["F", "M", "O"]
    nacimiento: Annotated[int, Gt(0)]
    fecha_creacion: int | None = get_unix_now()


class ActualizarUsuario(BaseUsuario):
    nombre: str
    ci: Annotated[int, Gt(1_000_000)]
    telefono: str
    correo: str
    genero: str
    nacimiento: int
