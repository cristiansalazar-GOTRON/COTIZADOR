from __future__ import annotations

from dataclasses import asdict

from .calculos import cotizacion_importacion, cotizacion_local, cotizacion_reparacion
from .config import (
    cargar_configuracion,
    cargar_ultima_cotizacion,
    guardar_configuracion,
    guardar_ultima_cotizacion,
)
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
    configuracion: Configuracion | None = None,
    guardar_formulario: bool = False,
) -> ResultadoCotizacion:
    if guardar_formulario:
        guardar_ultima_cotizacion(UltimaCotizacion(tipo="importacion", valores=asdict(entrada)))
    return cotizacion_importacion(entrada, configuracion or cargar_configuracion())


def generar_cotizacion_local(
    entrada: CotizacionLocalInput,
    configuracion: Configuracion | None = None,
    guardar_formulario: bool = False,
) -> ResultadoCotizacion:
    if guardar_formulario:
        guardar_ultima_cotizacion(UltimaCotizacion(tipo="local", valores=asdict(entrada)))
    return cotizacion_local(entrada, configuracion or cargar_configuracion())


def generar_cotizacion_reparacion(
    entrada: CotizacionReparacionInput,
    configuracion: Configuracion | None = None,
    guardar_formulario: bool = False,
) -> ResultadoCotizacion:
    if guardar_formulario:
        guardar_ultima_cotizacion(UltimaCotizacion(tipo="reparacion", valores=asdict(entrada)))
    return cotizacion_reparacion(entrada, configuracion or cargar_configuracion())


def obtener_configuracion() -> Configuracion:
    return cargar_configuracion()


def actualizar_configuracion(configuracion: Configuracion) -> None:
    guardar_configuracion(configuracion)


def obtener_ultima_cotizacion() -> UltimaCotizacion | None:
    return cargar_ultima_cotizacion()
