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


def cotizacion_importacion(
    entrada: CotizacionImportacionInput,
    configuracion: Configuracion,
) -> ResultadoCotizacion:
    asegurar_no_negativo(entrada.precio, "precio")
    asegurar_no_negativo(entrada.flete, "flete")
    asegurar_no_negativo(entrada.peso, "peso")
    _validar_configuracion(configuracion)

    resultado = ResultadoCotizacion()
    moneda_original = entrada.moneda.upper()
    modo_flete_importacion = validar_modo_flete_local(entrada.flete_modo)

    resultado.agregar_paso("Precio del producto", entrada.precio, moneda_original)

    if modo_flete_importacion == "porcentaje":
        valor_flete = aplicar_porcentaje(entrada.precio, entrada.flete)
        descripcion_flete = f"Valor del flete ({entrada.flete:.2f}%)"
    else:
        valor_flete = entrada.flete
        descripcion_flete = "Valor del flete"

    resultado.agregar_paso(descripcion_flete, valor_flete, moneda_original)

    subtotal_moneda = entrada.precio + valor_flete
    resultado.agregar_paso("Subtotal en moneda original", subtotal_moneda, moneda_original)

    subtotal_cop = convertir_a_cop(
        subtotal_moneda,
        entrada.moneda,
        configuracion.tasa_usd,
        configuracion.tasa_eur,
    )
    resultado.agregar_paso("Subtotal convertido a COP", subtotal_cop, "COP")

    valor_ganancia = aplicar_porcentaje(subtotal_cop, configuracion.ganancia_importacion)
    resultado.agregar_paso("Valor de la ganancia en COP", valor_ganancia, "COP")

    total = subtotal_cop + valor_ganancia

    valor_en_usd = convertir_a_usd(
        subtotal_moneda,
        entrada.moneda,
        configuracion.tasa_usd,
        configuracion.tasa_eur,
    )
    if valor_en_usd > configuracion.umbral_usd:
        resultado.agregar_paso("Recargo por valor alto", configuracion.recargo_valor_alto, "COP")
        total += configuracion.recargo_valor_alto
        resultado.agregar_paso("Subtotal despues de recargo por valor alto", total, "COP")

    if entrada.peso > configuracion.umbral_peso:
        resultado.agregar_paso("Recargo por peso", configuracion.recargo_peso, "COP")
        total += configuracion.recargo_peso
        resultado.agregar_paso("Subtotal despues de recargo por peso", total, "COP")

    resultado.agregar_paso("Subtotal antes de IVA en COP", total, "COP")

    valor_iva = aplicar_porcentaje(total, configuracion.iva)
    resultado.agregar_paso("Valor del IVA en COP", valor_iva, "COP")

    total += valor_iva
    resultado.agregar_paso("Total con IVA", total, "COP")
    return resultado


def cotizacion_local(entrada: CotizacionLocalInput, configuracion: Configuracion) -> ResultadoCotizacion:
    asegurar_no_negativo(entrada.precio_base_cop, "precio_base_cop")
    _validar_configuracion(configuracion)

    resultado = ResultadoCotizacion()
    resultado.agregar_paso("Precio base en COP", entrada.precio_base_cop, "COP")

    total = entrada.precio_base_cop + aplicar_flete_local(
        entrada.precio_base_cop,
        configuracion.flete_local,
        configuracion.flete_local_modo,
    )
    resultado.agregar_paso("Subtotal con flete local", total, "COP")

    total += aplicar_porcentaje(total, configuracion.ganancia_local)
    resultado.agregar_paso("Subtotal con ganancia local", total, "COP")

    total += aplicar_porcentaje(total, configuracion.iva)
    resultado.agregar_paso("Total con IVA", total, "COP")
    return resultado


def cotizacion_reparacion(
    entrada: CotizacionReparacionInput,
    configuracion: Configuracion,
) -> ResultadoCotizacion:
    asegurar_no_negativo(entrada.precio_base_usd, "precio_base_usd")
    asegurar_no_negativo(entrada.peso, "peso")
    _validar_configuracion(configuracion)

    resultado = ResultadoCotizacion()
    precio_cop = convertir_a_cop(entrada.precio_base_usd, "USD", configuracion.tasa_usd, configuracion.tasa_eur)
    resultado.agregar_paso("Precio convertido a COP", precio_cop, "COP")

    total = precio_cop + aplicar_porcentaje(precio_cop, configuracion.flete_reparacion)
    resultado.agregar_paso("Subtotal con flete de reparacion", total, "COP")

    total += aplicar_porcentaje(total, configuracion.ganancia_reparacion)
    resultado.agregar_paso("Subtotal con ganancia de reparacion", total, "COP")

    if entrada.precio_base_usd > configuracion.umbral_usd:
        total += configuracion.recargo_valor_alto
        resultado.agregar_paso("Subtotal con recargo por valor alto", total, "COP")

    if entrada.peso > configuracion.umbral_peso:
        total += configuracion.recargo_peso
        resultado.agregar_paso("Subtotal con recargo por peso", total, "COP")

    total += aplicar_porcentaje(total, configuracion.iva)
    resultado.agregar_paso("Total con IVA", total, "COP")
    return resultado
