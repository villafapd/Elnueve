from dataclasses import dataclass

@dataclass
class HorayFecha:
    hora: int
    minutos: int
    segundos: int
    dia: int
    mes: int
    ano: int
    microsegundos: int
    diasemana: str
    semanaano: str
    milliseg: int
    hora_inicio: bool