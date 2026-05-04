"""Modelos de datos del simulador."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional


TipoTCL = Literal["mayor", "menor", "entre", "suma_mayor"]


@dataclass(frozen=True)
class CasoTCL:
    ref: str
    escenario: str
    mu: float
    sigma: float
    n: int
    tipo: TipoTCL
    limite: Optional[float] = None
    limite_inferior: Optional[float] = None
    limite_superior: Optional[float] = None
    unidad: str = ""
    contexto: str = ""


@dataclass(frozen=True)
class CasoICMedia:
    nombre: str
    n: int
    media_muestral: float
    sigma: Optional[float] = None
    s: Optional[float] = None
    confianza: float = 0.95
    unidad: str = ""
    contexto: str = ""


@dataclass(frozen=True)
class CasoICProporcion:
    nombre: str
    n: int
    x: int
    confianza: float = 0.95
    contexto: str = ""


@dataclass(frozen=True)
class ResultadoTCL:
    ref: str
    escenario: str
    pregunta: str
    se: float
    z: str
    probabilidad: float
    procedimiento: str
    interpretacion: str


@dataclass(frozen=True)
class ResultadoIC:
    caso: str
    modelo: str
    razon: str
    estimador: float
    se: float
    valor_critico: float
    margen_error: float
    limite_inferior: float
    limite_superior: float
    formula: str
    recomendacion: str
    es_proporcion: bool = False
