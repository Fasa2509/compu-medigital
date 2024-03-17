from typing import Optional
from pydantic import BaseModel


intervals = (
    ('semanas', 604800),  # 60 * 60 * 24 * 7
    ('días', 86400),    # 60 * 60 * 24
    ('horas', 3600),    # 60 * 60
    ('minutos', 60),
    ('segundos', 1),
)


def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])


class BaseTratamiento(BaseModel):
    pass


class Tratamiento(BaseTratamiento):
    id: int
    indicaciones: str
    duracion: Optional[int]
    diagnostico_id: int


def TratamientoFactory(data: list[str]):
    id, indicaciones, duracion, diagnostico_id = data

    return {
        "id": id,
        "indicaciones": indicaciones,
        "duracion": duracion,
        "diagnostico_id": diagnostico_id,
    }


def TratamientoFactoryDates(data: list[str]):
    id, indicaciones, duracion, diagnostico_id = data

    duracion = display_time(duracion) if duracion else "---"

    return {
        "id": id,
        "indicaciones": indicaciones,
        "duracion": duracion,
        "diagnostico_id": diagnostico_id,
    }


class NuevoTratamiento(BaseTratamiento):
    indicaciones: str
    duracion: Optional[int]
    diagnostico_id: int
