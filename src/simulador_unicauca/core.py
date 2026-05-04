"""Motor estadístico principal del proyecto."""

from __future__ import annotations

from math import sqrt

from .distributions import normal_cdf, valor_critico_t, valor_critico_z
from .models import CasoICMedia, CasoICProporcion, CasoTCL, ResultadoIC, ResultadoTCL
from .recommendations import recomendacion_media, recomendacion_proporcion


class SimuladorUnicauca:
    """Clase principal solicitada para el proyecto."""

    @staticmethod
    def error_muestra(media_muestral_observada: float, mu: float) -> float:
        return media_muestral_observada - mu

    @staticmethod
    def error_estandar_media(sigma: float, n: int) -> float:
        if sigma <= 0:
            raise ValueError("sigma debe ser positiva.")
        if n <= 0:
            raise ValueError("n debe ser positivo.")
        return sigma / sqrt(n)

    def resolver_tcl(self, caso: CasoTCL) -> ResultadoTCL:
        se = self.error_estandar_media(caso.sigma, caso.n)

        if caso.tipo == "mayor":
            if caso.limite is None:
                raise ValueError("Debe indicar un límite.")
            z = (caso.limite - caso.mu) / se
            prob = 1 - normal_cdf(z)
            pregunta = f"P(X̄ > {caso.limite})"
            procedimiento = f"Z = ({caso.limite} - {caso.mu}) / ({caso.sigma}/√{caso.n}) = {z:.4f}"
            z_texto = f"{z:.4f}"

        elif caso.tipo == "menor":
            if caso.limite is None:
                raise ValueError("Debe indicar un límite.")
            z = (caso.limite - caso.mu) / se
            prob = normal_cdf(z)
            pregunta = f"P(X̄ < {caso.limite})"
            procedimiento = f"Z = ({caso.limite} - {caso.mu}) / ({caso.sigma}/√{caso.n}) = {z:.4f}"
            z_texto = f"{z:.4f}"

        elif caso.tipo == "entre":
            if caso.limite_inferior is None or caso.limite_superior is None:
                raise ValueError("Debe indicar límite inferior y superior.")
            z1 = (caso.limite_inferior - caso.mu) / se
            z2 = (caso.limite_superior - caso.mu) / se
            prob = normal_cdf(z2) - normal_cdf(z1)
            pregunta = f"P({caso.limite_inferior} < X̄ < {caso.limite_superior})"
            procedimiento = (
                f"Z1 = ({caso.limite_inferior} - {caso.mu}) / ({caso.sigma}/√{caso.n}) = {z1:.4f}; "
                f"Z2 = ({caso.limite_superior} - {caso.mu}) / ({caso.sigma}/√{caso.n}) = {z2:.4f}"
            )
            z_texto = f"{z1:.4f} a {z2:.4f}"

        elif caso.tipo == "suma_mayor":
            if caso.limite is None:
                raise ValueError("Debe indicar un límite.")
            media_suma = caso.n * caso.mu
            sd_suma = caso.sigma * sqrt(caso.n)
            z = (caso.limite - media_suma) / sd_suma
            prob = 1 - normal_cdf(z)
            pregunta = f"P(Suma > {caso.limite})"
            procedimiento = (
                f"E(S)=nμ={caso.n}×{caso.mu}={media_suma:.4f}; "
                f"SD(S)=σ√n={caso.sigma}√{caso.n}={sd_suma:.4f}; "
                f"Z=({caso.limite}-{media_suma:.4f})/{sd_suma:.4f}={z:.4f}"
            )
            z_texto = f"{z:.4f}"

        else:
            raise ValueError(f"Tipo TCL no reconocido: {caso.tipo}")

        interpretacion = (
            "Se usa el Teorema Central del Límite porque se analiza una media muestral "
            "o una suma de observaciones. La dispersión relevante es el Error Estándar SE = σ/√n."
        )

        return ResultadoTCL(caso.ref, caso.escenario, pregunta, se, z_texto, prob, procedimiento, interpretacion)

    @staticmethod
    def elegir_modelo_ic_media(caso: CasoICMedia) -> str:
        if caso.sigma is not None:
            return "Z"
        if caso.s is None:
            raise ValueError("Debe proporcionar s cuando σ es desconocida.")
        if caso.n < 30:
            return "t"
        return "Z_aproximada"

    def intervalo_media(self, caso: CasoICMedia, meta: float | None = None) -> ResultadoIC:
        if caso.n <= 0:
            raise ValueError("n debe ser positivo.")

        modelo = self.elegir_modelo_ic_media(caso)

        if modelo == "Z":
            crit = valor_critico_z(caso.confianza)
            se = caso.sigma / sqrt(caso.n)
            nombre_modelo = "Distribución Z"
            razon = "Se usa Z porque la desviación estándar poblacional σ es conocida."
            formula = f"IC = x̄ ± Z(σ/√n) = {caso.media_muestral} ± {crit:.4f}({caso.sigma}/√{caso.n})"
        elif modelo == "t":
            crit = valor_critico_t(caso.confianza, caso.n - 1)
            se = caso.s / sqrt(caso.n)
            nombre_modelo = f"Distribución t de Student, gl={caso.n - 1}"
            razon = "Se usa t porque σ es desconocida, se estima con s y la muestra es pequeña."
            formula = f"IC = x̄ ± t(s/√n) = {caso.media_muestral} ± {crit:.4f}({caso.s}/√{caso.n})"
        else:
            crit = valor_critico_z(caso.confianza)
            se = caso.s / sqrt(caso.n)
            nombre_modelo = "Distribución Z aproximada"
            razon = "Se usa Z aproximada porque σ es desconocida pero n es grande."
            formula = f"IC = x̄ ± Z(s/√n) = {caso.media_muestral} ± {crit:.4f}({caso.s}/√{caso.n})"

        margen = crit * se
        li = caso.media_muestral - margen
        ls = caso.media_muestral + margen

        return ResultadoIC(
            caso=caso.nombre,
            modelo=nombre_modelo,
            razon=razon,
            estimador=caso.media_muestral,
            se=se,
            valor_critico=crit,
            margen_error=margen,
            limite_inferior=li,
            limite_superior=ls,
            formula=formula,
            recomendacion=recomendacion_media(caso.contexto, li, ls, caso.unidad, meta),
            es_proporcion=False,
        )

    def intervalo_proporcion(self, caso: CasoICProporcion, meta: float | None = None) -> ResultadoIC:
        if caso.n <= 0:
            raise ValueError("n debe ser positivo.")
        if caso.x < 0 or caso.x > caso.n:
            raise ValueError("x debe estar entre 0 y n.")

        p_hat = caso.x / caso.n
        crit = valor_critico_z(caso.confianza)
        se = sqrt(p_hat * (1 - p_hat) / caso.n)
        margen = crit * se
        li = max(0.0, p_hat - margen)
        ls = min(1.0, p_hat + margen)

        formula = f"p̂ = x/n = {caso.x}/{caso.n} = {p_hat:.4f}; IC = p̂ ± Z√(p̂(1-p̂)/n)"

        return ResultadoIC(
            caso=caso.nombre,
            modelo="Modelo Z para proporciones",
            razon="Se usa proporciones porque el parámetro poblacional es p y se estima con p̂=x/n.",
            estimador=p_hat,
            se=se,
            valor_critico=crit,
            margen_error=margen,
            limite_inferior=li,
            limite_superior=ls,
            formula=formula,
            recomendacion=recomendacion_proporcion(caso.contexto, li, ls, meta),
            es_proporcion=True,
        )
