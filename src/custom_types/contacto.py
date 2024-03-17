from typing import Literal, List
from pydantic import BaseModel


class BaseContacto(BaseModel):
    pass


class Contacto(BaseContacto):
    id: int
    nombre: str
    ci: int
    correo: str
    relacion: str
    telefono: str
    genero: Literal["F", "M", "O"]
    nacimiento: int
    paciente_id: int


def ContactoFactory(data: List[str]):
    id, nombre, ci, correo, relacion, telefono, genero, nacimiento = data

    return {
        "id": id,
        "nombre": nombre,
        "ci": ci,
        "correo": correo,
        "relacion": relacion,
        "telefono": telefono,
        "genero": genero,
        "nacimiento": nacimiento,
    }


class NuevoContacto(BaseContacto):
    nombre: str
    ci: int
    correo: str
    relacion: str
    telefono: str
    genero: Literal["F", "M", "O"]
    nacimiento: int
    paciente_id: int


class ActualizarContacto(BaseContacto):
    id: int
    nombre: str
    ci: int
    correo: str
    telefono: str
