from typing import Literal
from pydantic import BaseModel


class BaseContactoEnPaciente(BaseModel):
    pass


class ContactoEnPaciente(BaseContactoEnPaciente):
    id: int
    paciente_id: int
    contacto_id: int


class NuevoContactoEnPaciente(BaseContactoEnPaciente):
    paciente_id: int
    contacto_id: int
