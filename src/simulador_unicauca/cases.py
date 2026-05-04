"""Casos precargados del documento académico."""

from __future__ import annotations

from .models import CasoICMedia, CasoICProporcion, CasoTCL


def casos_tcl_documento() -> list[CasoTCL]:
    return [
        CasoTCL("TCL-1", "CEO-Energía", 180, 45, 40, "mayor", limite=195, unidad="kWh", contexto="Consumo energético en hogares de Popayán."),
        CasoTCL("TCL-2", "Banca Local", 12, 4, 50, "menor", limite=10.5, unidad="min", contexto="Tiempo de atención en ventanilla bancaria."),
        CasoTCL("TCL-3", "Servi-Logística", 20, 5, 35, "suma_mayor", limite=750, unidad="kg", contexto="Riesgo de exceder el límite de carga."),
        CasoTCL("TCL-4", "Sueldos", 2.5, 0.8, 100, "entre", limite_inferior=2.3, limite_superior=2.7, unidad="M COP", contexto="Ingresos medios del sector comercio."),
        CasoTCL("TCL-5", "Café del Cauca", 500, 10, 45, "mayor", limite=503, unidad="g", contexto="Peso promedio de bolsas de café de exportación."),
    ]


def casos_ic_media_documento() -> list[CasoICMedia]:
    return [
        CasoICMedia("Fibras textiles", 40, 50, sigma=4, unidad="resistencia", contexto="Resistencia de fibras en textiles de la región."),
        CasoICMedia("Fletes intermunicipales", 35, 1.2, sigma=0.2, unidad="M COP", contexto="Costos operativos de fletes intermunicipales."),
        CasoICMedia("Empaques retail", 50, 22, sigma=1.5, unidad="peso", contexto="Peso neto de empaques para retail nacional."),
        CasoICMedia("Mochilas artesanales", 15, 22, s=4, unidad="mochilas", contexto="Producción artesanal de mochilas."),
        CasoICMedia("Marketing PyMEs", 10, 3.5, s=0.8, unidad="M COP", contexto="Presupuesto mensual de marketing en PyMEs."),
        CasoICMedia("Incapacidad planta", 12, 18, s=3.5, unidad="días", contexto="Días de incapacidad en planta de producción."),
    ]


def casos_ic_proporcion_documento() -> list[CasoICProporcion]:
    return [
        CasoICProporcion("Aceptación gaseosa", 1000, 450, contexto="Nivel de aceptación de nueva marca de gaseosa."),
        CasoICProporcion("Fallos software", 500, 15, contexto="Tasa de fallos en software de inventarios."),
        CasoICProporcion("Modalidad híbrida", 250, 180, contexto="Empleados que prefieren modalidad híbrida."),
    ]
