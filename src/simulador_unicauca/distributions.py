"""Distribuciones estadísticas con Python estándar.

No se usa scipy para evitar problemas de instalación en Windows.
"""

from __future__ import annotations

from math import exp, pi, sqrt
from statistics import NormalDist

_NORMAL = NormalDist(mu=0, sigma=1)


def normal_pdf(x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
    if sigma <= 0:
        raise ValueError("sigma debe ser positiva.")
    return (1.0 / (sigma * sqrt(2 * pi))) * exp(-0.5 * ((x - mu) / sigma) ** 2)


def normal_cdf(z: float) -> float:
    return _NORMAL.cdf(z)


def normal_ppf(p: float) -> float:
    if not 0 < p < 1:
        raise ValueError("p debe estar entre 0 y 1.")
    return _NORMAL.inv_cdf(p)


def valor_critico_z(confianza: float) -> float:
    alpha = 1 - confianza
    return normal_ppf(1 - alpha / 2)


_T_95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
    6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
    11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
    16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
    21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060,
    26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042,
}

_T_90 = {
    1: 6.314, 2: 2.920, 3: 2.353, 4: 2.132, 5: 2.015,
    6: 1.943, 7: 1.895, 8: 1.860, 9: 1.833, 10: 1.812,
    11: 1.796, 12: 1.782, 13: 1.771, 14: 1.761, 15: 1.753,
    16: 1.746, 17: 1.740, 18: 1.734, 19: 1.729, 20: 1.725,
    21: 1.721, 22: 1.717, 23: 1.714, 24: 1.711, 25: 1.708,
    26: 1.706, 27: 1.703, 28: 1.701, 29: 1.699, 30: 1.697,
}

_T_99 = {
    1: 63.657, 2: 9.925, 3: 5.841, 4: 4.604, 5: 4.032,
    6: 3.707, 7: 3.499, 8: 3.355, 9: 3.250, 10: 3.169,
    11: 3.106, 12: 3.055, 13: 3.012, 14: 2.977, 15: 2.947,
    16: 2.921, 17: 2.898, 18: 2.878, 19: 2.861, 20: 2.845,
    21: 2.831, 22: 2.819, 23: 2.807, 24: 2.797, 25: 2.787,
    26: 2.779, 27: 2.771, 28: 2.763, 29: 2.756, 30: 2.750,
}


def valor_critico_t(confianza: float, gl: int) -> float:
    if gl <= 0:
        raise ValueError("Los grados de libertad deben ser positivos.")
    if gl > 30:
        return valor_critico_z(confianza)

    key = round(confianza, 2)
    tablas = {0.90: _T_90, 0.95: _T_95, 0.99: _T_99}
    if key not in tablas:
        raise ValueError("Confianza soportada para t: 0.90, 0.95 o 0.99.")
    return tablas[key][gl]
