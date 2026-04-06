from __future__ import annotations

from dataclasses import asdict

from .calculos import cotizacion_importacion, cotizacion_local, cotizacion_reparacion
from .config import guardar_ultima_cotizacion
from .modelos import (
    Configuracion,
    CotizacionImportacionInput,
    CotizacionLocalInput,
    CotizacionReparacionInput,
    ResultadoCotizacion,
    UltimaCotizacion,
)


def generar_cotizacion_importacion(
    entrada: CotizacionImportacionInput,
    configuracion: Configuracion,
    guardar_formulario: bool = False,
) -> ResultadoCotizacion:
    if guardar_formulario:
        guardar_ultima_cotizacion(UltimaCotizacion(tipo="importacion", valores=asdict(entrada)))
    return cotizacion_importacion(entrada, configuracion)


def generar_cotizacion_local(
    entrada: CotizacionLocalInput,
    configuracion: Configuracion,
    guardar_formulario: bool = False,
) -> ResultadoCotizacion:
    if guardar_formulario:
        guardar_ultima_cotizacion(UltimaCotizacion(tipo="local", valores=asdict(entrada)))
    return cotizacion_local(entrada, configuracion)


def generar_cotizacion_reparacion(
    entrada: CotizacionReparacionInput,
    configuracion: Configuracion,
    guardar_formulario: bool = False,
) -> ResultadoCotizacion:
    if guardar_formulario:
        guardar_ultima_cotizacion(UltimaCotizacion(tipo="reparacion", valores=asdict(entrada)))
    return cotizacion_reparacion(entrada, configuracion)
