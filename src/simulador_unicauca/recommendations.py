"""Recomendaciones gerenciales automáticas."""

from __future__ import annotations


def recomendacion_media(contexto: str, li: float, ls: float, unidad: str, meta: float | None = None) -> str:
    contexto = contexto.lower()

    if meta is not None:
        if li > meta:
            return f"Incluso el límite inferior ({li:.4f} {unidad}) supera la meta ({meta:.4f} {unidad}). La evidencia es favorable."
        if ls < meta:
            return f"Incluso el límite superior ({ls:.4f} {unidad}) está por debajo de la meta ({meta:.4f} {unidad}). Conviene replantear la estrategia."
        return f"La meta ({meta:.4f} {unidad}) cae dentro del intervalo. Hay incertidumbre; conviene ampliar la muestra."

    if "fibras" in contexto:
        return f"Gestionar calidad considerando una resistencia media real entre {li:.2f} y {ls:.2f} {unidad}."
    if "fletes" in contexto:
        return f"Cotizar con prudencia usando el límite superior {ls:.3f} {unidad} para evitar subestimar costos."
    if "empaques" in contexto:
        return f"Comparar el límite inferior {li:.2f} {unidad} con el estándar mínimo de empaque."
    if "mochilas" in contexto:
        return f"Recolectar más datos antes de fijar metas; la media plausible está entre {li:.2f} y {ls:.2f} {unidad}."
    if "marketing" in contexto:
        return f"Planear caja entre {li:.2f} y {ls:.2f} {unidad}; usar el límite superior para presupuestos conservadores."
    if "incapacidad" in contexto:
        return f"Revisar prevención y turnos si el límite superior {ls:.2f} {unidad} afecta la capacidad productiva."

    return f"El promedio poblacional plausible está entre {li:.4f} y {ls:.4f} {unidad}. Use el límite más desfavorable para decisiones prudentes."


def recomendacion_proporcion(contexto: str, li: float, ls: float, meta: float | None = None) -> str:
    contexto = contexto.lower()

    if meta is not None:
        if meta > 1:
            meta = meta / 100
        if li > meta:
            return f"Incluso el límite inferior ({li:.2%}) supera la meta ({meta:.2%}). La evidencia favorece la decisión."
        if ls < meta:
            return f"Incluso el límite superior ({ls:.2%}) está por debajo de la meta ({meta:.2%}). Conviene replantear la estrategia."
        return f"La meta ({meta:.2%}) cae dentro del intervalo; existe incertidumbre y conviene recolectar más datos."

    if "gaseosa" in contexto:
        return f"La aceptación real podría estar entre {li:.2%} y {ls:.2%}. Si la meta es superar 50%, se recomienda cautela."
    if "fallos" in contexto or "software" in contexto:
        return f"La tasa real de fallos podría estar entre {li:.2%} y {ls:.2%}; dimensionar soporte con el límite superior."
    if "híbrida" in contexto or "hibrida" in contexto:
        return f"La preferencia híbrida podría estar entre {li:.2%} y {ls:.2%}; conviene formalizar una política híbrida."

    return f"La proporción poblacional plausible está entre {li:.2%} y {ls:.2%}."
