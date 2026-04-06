from __future__ import annotations


class CotizadorError(Exception):
    """Base exception for quotation backend errors."""


class ValidacionError(CotizadorError):
    """Raised when an input value or configuration is invalid."""


def asegurar_no_negativo(valor: float, nombre: str) -> float:
    if valor < 0:
        raise ValidacionError(f"El valor '{nombre}' no puede ser negativo.")
    return valor


def asegurar_positivo(valor: float, nombre: str) -> float:
    if valor <= 0:
        raise ValidacionError(f"El valor '{nombre}' debe ser mayor a 0.")
    return valor


def validar_moneda(moneda: str) -> str:
    moneda_normalizada = moneda.strip().upper()
    if moneda_normalizada not in {"COP", "USD", "EUR"}:
        raise ValidacionError("La moneda debe ser 'COP', 'USD' o 'EUR'.")
    return moneda_normalizada


def validar_modo_flete_local(modo: str) -> str:
    modo_normalizado = modo.strip().lower()
    if modo_normalizado not in {"porcentaje", "fijo"}:
        raise ValidacionError("El modo de flete local debe ser 'porcentaje' o 'fijo'.")
    return modo_normalizado


def aplicar_porcentaje(base: float, porcentaje: float) -> float:
    asegurar_no_negativo(base, "base")
    asegurar_no_negativo(porcentaje, "porcentaje")
    return base * (porcentaje / 100.0)


def convertir_a_cop(valor: float, moneda: str, tasa_usd: float, tasa_eur: float) -> float:
    asegurar_no_negativo(valor, "valor")
    moneda_normalizada = validar_moneda(moneda)
    asegurar_positivo(tasa_usd, "tasa_usd")
    asegurar_positivo(tasa_eur, "tasa_eur")

    if moneda_normalizada == "COP":
        return valor
    if moneda_normalizada == "USD":
        return valor * tasa_usd
    return valor * tasa_eur


def convertir_a_usd(valor: float, moneda: str, tasa_usd: float, tasa_eur: float) -> float:
    asegurar_no_negativo(valor, "valor")
    moneda_normalizada = validar_moneda(moneda)
    asegurar_positivo(tasa_usd, "tasa_usd")
    asegurar_positivo(tasa_eur, "tasa_eur")

    if moneda_normalizada == "COP":
        return valor / tasa_usd
    if moneda_normalizada == "USD":
        return valor
    return (valor * tasa_eur) / tasa_usd


def aplicar_flete_local(base: float, flete_local: float, modo: str) -> float:
    asegurar_no_negativo(base, "precio_base")
    asegurar_no_negativo(flete_local, "flete_local")
    modo_normalizado = validar_modo_flete_local(modo)

    if modo_normalizado == "porcentaje":
        return aplicar_porcentaje(base, flete_local)
    return flete_local
