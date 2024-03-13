from pydantic import BaseModel


class BaseTratamiento(BaseModel):
    pass


class Tratamiento(BaseTratamiento):
    id: int
    indicaciones: str
    duracion: int | None
    diagnostico_id: int


def TratamientoFactory(data: list[str]):
    id, indicaciones, duracion, diagnostico_id = data

    return {
        "id": id,
        "indicaciones": indicaciones,
        "duracion": duracion,
        "diagnostico_id": diagnostico_id,
    }


class NuevoTratamiento(BaseTratamiento):
    indicaciones: str
    duracion: int | None
    diagnostico_id: int
