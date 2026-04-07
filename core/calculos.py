from __future__ import annotations

if __package__ in {None, ""}:
    raise SystemExit(
        "Este modulo no se ejecuta directamente.\n"
        "Usa una de estas opciones desde la raiz del proyecto:\n"
        '  .\\.venv\\Scripts\\python.exe main.py\n'
        '  .\\.venv\\Scripts\\python.exe -m core\n'
        '  .\\.venv\\Scripts\\python.exe -m pytest tests\\test_backend.py -q'
    )

from .modelos import (
    Configuracion,
    CotizacionImportacionInput,
    CotizacionLocalInput,
    CotizacionReparacionInput,
    ResultadoCotizacion,
)
from .utils import (
    aplicar_flete_local,
    aplicar_porcentaje,
    asegurar_no_negativo,
    convertir_a_cop,
    convertir_a_usd,
    validar_modo_flete_local,
)


def _validar_configuracion(configuracion: Configuracion) -> None:
    for nombre, valor in configuracion.to_dict().items():
        if isinstance(valor, str):
            continue
        asegurar_no_negativo(valor, nombre)
    validar_modo_flete_local(configuracion.flete_local_modo)
    validar_modo_flete_local(configuracion.flete_reparacion_modo)


def cotizacion_importacion(
    entrada: CotizacionImportacionInput,
    configuracion: Configuracion,
) -> ResultadoCotizacion:
    asegurar_no_negativo(entrada.precio, "precio")
    asegurar_no_negativo(entrada.flete, "flete")
    asegurar_no_negativo(entrada.peso, "peso")
    asegurar_no_negativo(entrada.ganancia_porcentaje, "ganancia_porcentaje")
    asegurar_no_negativo(entrada.iva_porcentaje, "iva_porcentaje")
    _validar_configuracion(configuracion)
    tasa_usd = entrada.tasa_usd if entrada.tasa_usd is not None else configuracion.tasa_usd
    tasa_eur = entrada.tasa_eur if entrada.tasa_eur is not None else configuracion.tasa_eur
    asegurar_no_negativo(tasa_usd, "tasa_usd")
    asegurar_no_negativo(tasa_eur, "tasa_eur")

    resultado = ResultadoCotizacion()
    moneda_original = entrada.moneda.upper()
    modo_flete_importacion = validar_modo_flete_local(entrada.flete_modo)

    resultado.agregar_paso("Precio del producto", entrada.precio, moneda_original)

    if modo_flete_importacion == "porcentaje":
        valor_flete = aplicar_porcentaje(entrada.precio, entrada.flete)
    else:
        valor_flete = entrada.flete

    resultado.agregar_paso("Calculo del flete", valor_flete, moneda_original)

    subtotal_moneda = entrada.precio + valor_flete
    resultado.agregar_paso("Subtotal en moneda original", subtotal_moneda, moneda_original)

    subtotal_cop = convertir_a_cop(
        subtotal_moneda,
        entrada.moneda,
        tasa_usd,
        tasa_eur,
    )
    resultado.agregar_paso("Conversion a COP", subtotal_cop, "COP")

    valor_ganancia = aplicar_porcentaje(subtotal_cop, entrada.ganancia_porcentaje)
    resultado.agregar_paso("Calculo de ganancia en COP", valor_ganancia, "COP")

    total = subtotal_cop + valor_ganancia

    valor_en_usd = convertir_a_usd(
        subtotal_moneda,
        entrada.moneda,
        tasa_usd,
        tasa_eur,
    )
    if valor_en_usd > configuracion.umbral_usd:
        resultado.agregar_paso("Recargo por valor alto", configuracion.recargo_valor_alto, "COP")
        total += configuracion.recargo_valor_alto

    if entrada.peso > configuracion.umbral_peso:
        resultado.agregar_paso("Recargo por peso", configuracion.recargo_peso, "COP")
        total += configuracion.recargo_peso

    resultado.agregar_paso("Subtotal antes de IVA", total, "COP")

    valor_iva = aplicar_porcentaje(total, entrada.iva_porcentaje)
    resultado.agregar_paso("IVA", valor_iva, "COP")

    total += valor_iva
    resultado.agregar_paso("Total final", total, "COP")
    return resultado


def cotizacion_local(entrada: CotizacionLocalInput, configuracion: Configuracion) -> ResultadoCotizacion:
    asegurar_no_negativo(entrada.precio_base_cop, "precio_base_cop")
    asegurar_no_negativo(entrada.flete_local, "flete_local")
    asegurar_no_negativo(entrada.ganancia_porcentaje, "ganancia_porcentaje")
    asegurar_no_negativo(entrada.iva_porcentaje, "iva_porcentaje")
    _validar_configuracion(configuracion)

    resultado = ResultadoCotizacion()
    resultado.agregar_paso("Precio base en COP", entrada.precio_base_cop, "COP")

    total = entrada.precio_base_cop + aplicar_flete_local(
        entrada.precio_base_cop,
        entrada.flete_local,
        entrada.flete_modo,
    )
    resultado.agregar_paso("Subtotal con flete local", total, "COP")

    valor_ganancia = aplicar_porcentaje(total, entrada.ganancia_porcentaje)
    resultado.agregar_paso("Valor de la ganancia local en COP", valor_ganancia, "COP")
    total += valor_ganancia
    resultado.agregar_paso("Subtotal antes de IVA en COP", total, "COP")

    valor_iva = aplicar_porcentaje(total, entrada.iva_porcentaje)
    resultado.agregar_paso("Valor del IVA en COP", valor_iva, "COP")
    total += valor_iva
    resultado.agregar_paso("Total con IVA", total, "COP")
    return resultado


def cotizacion_reparacion(
    entrada: CotizacionReparacionInput,
    configuracion: Configuracion,
) -> ResultadoCotizacion:
    asegurar_no_negativo(entrada.precio_base, "precio_base")
    asegurar_no_negativo(entrada.flete_reparacion, "flete_reparacion")
    asegurar_no_negativo(entrada.ganancia_porcentaje, "ganancia_porcentaje")
    asegurar_no_negativo(entrada.iva_porcentaje, "iva_porcentaje")
    asegurar_no_negativo(entrada.peso, "peso")
    _validar_configuracion(configuracion)
    tasa_usd = entrada.tasa_usd if entrada.tasa_usd is not None else configuracion.tasa_usd
    tasa_eur = entrada.tasa_eur if entrada.tasa_eur is not None else configuracion.tasa_eur
    asegurar_no_negativo(tasa_usd, "tasa_usd")
    asegurar_no_negativo(tasa_eur, "tasa_eur")

    resultado = ResultadoCotizacion()
    moneda_original = entrada.moneda.upper()
    resultado.agregar_paso("Precio del producto", entrada.precio_base, moneda_original)
    precio_cop = convertir_a_cop(entrada.precio_base, entrada.moneda, tasa_usd, tasa_eur)
    resultado.agregar_paso("Conversion a COP", precio_cop, "COP")

    total = precio_cop + aplicar_flete_local(
        precio_cop,
        entrada.flete_reparacion,
        entrada.flete_modo,
    )
    resultado.agregar_paso("Subtotal con flete de reparacion", total, "COP")

    valor_ganancia = aplicar_porcentaje(total, entrada.ganancia_porcentaje)
    resultado.agregar_paso("Valor de la ganancia de reparacion en COP", valor_ganancia, "COP")
    total += valor_ganancia

    valor_en_usd = convertir_a_usd(entrada.precio_base, entrada.moneda, tasa_usd, tasa_eur)
    if valor_en_usd > configuracion.umbral_usd:
        resultado.agregar_paso("Recargo por valor alto", configuracion.recargo_valor_alto, "COP")
        total += configuracion.recargo_valor_alto

    if entrada.peso > configuracion.umbral_peso:
        resultado.agregar_paso("Recargo por peso", configuracion.recargo_peso, "COP")
        total += configuracion.recargo_peso

    resultado.agregar_paso("Subtotal antes de IVA", total, "COP")
    valor_iva = aplicar_porcentaje(total, entrada.iva_porcentaje)
    resultado.agregar_paso("IVA", valor_iva, "COP")
    total += valor_iva
    resultado.agregar_paso("Total final", total, "COP")
    return resultado
