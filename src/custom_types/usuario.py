from typing import Annotated, Literal
from annotated_types import Gt
from pydantic import BaseModel, field_validator

from src.helpers.dates import get_unix_now


class BaseUsuario(BaseModel):
    pass


class Usuario(BaseUsuario):
    id: int
    nombre: str
    ci: Annotated[int, Gt(1_000_000)]
    telefono: str
    correo: str
    genero: str
    nacimiento: int
    fecha_creacion: int


class NuevoUsuario(BaseUsuario):
    nombre: str
    ci: Annotated[int, Gt(1_000_000)]
    telefono: str
    correo: str
    genero: Literal["F", "M", "O"]
    nacimiento: Annotated[int, Gt(0)]
    fecha_creacion: int | None = get_unix_now()
    clave: str | None = None


class ActualizarUsuario(BaseUsuario):
    nombre: str
    ci: Annotated[int, Gt(1_000_000)]
    telefono: str
