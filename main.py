from __future__ import annotations

from core.modelos import (
    Configuracion,
    CotizacionImportacionInput,
    CotizacionLocalInput,
    CotizacionReparacionInput,
    UltimaCotizacion,
)
from core.servicios import (
    generar_cotizacion_importacion,
    generar_cotizacion_local,
    generar_cotizacion_reparacion,
    obtener_configuracion,
    obtener_ultima_cotizacion,
)
from core.utils import CotizadorError


def formatear_valor(valor: float, moneda: str) -> str:
    return f"{valor:,.2f} {moneda}"


def imprimir_resultado(titulo: str, totalizador) -> None:
    print(f"\n{titulo}")
    for paso in totalizador.pasos:
        print(f"- {paso.descripcion}: {formatear_valor(paso.valor, paso.moneda)}")
    print(f"TOTAL FINAL: {formatear_valor(totalizador.total_final, 'COP')}")


def pedir_texto(mensaje: str, valor_por_defecto: str | None = None) -> str:
    sufijo = f" [{valor_por_defecto}]" if valor_por_defecto else ""
    while True:
        valor = input(f"{mensaje}{sufijo}: ").strip()
        if valor:
            return valor
        if valor_por_defecto is not None:
            return valor_por_defecto
        print("Debes ingresar un valor.")


def pedir_float(mensaje: str, valor_por_defecto: float | None = None) -> float:
    texto_defecto = None if valor_por_defecto is None else str(valor_por_defecto)
    while True:
        valor = pedir_texto(mensaje, texto_defecto).replace(",", ".")
        try:
            return float(valor)
        except ValueError:
            print("Ingresa un numero valido.")


def pedir_tipo_cotizacion() -> str:
    print("\nSelecciona el tipo de cotizacion:")
    print("1. Importacion")
    print("2. Local")
    print("3. Reparacion")

    equivalencias = {
        "1": "importacion",
        "2": "local",
        "3": "reparacion",
        "importacion": "importacion",
        "local": "local",
        "reparacion": "reparacion",
    }

    while True:
        opcion = input("Opcion: ").strip().lower()
        if opcion in equivalencias:
            return equivalencias[opcion]
        print("Opcion invalida. Elige 1, 2 o 3.")


def preguntar_si_no(mensaje: str, valor_por_defecto: bool = False) -> bool:
    defecto = "s" if valor_por_defecto else "n"
    while True:
        respuesta = input(f"{mensaje} [s/n] ({defecto}): ").strip().lower()
        if not respuesta:
            return valor_por_defecto
        if respuesta in {"s", "si", "y", "yes"}:
            return True
        if respuesta in {"n", "no"}:
            return False
        print("Responde con 's' o 'n'.")


def pedir_modo_flete_importacion(valor_por_defecto: str = "fijo") -> str:
    equivalencias = {
        "1": "fijo",
        "2": "porcentaje",
        "fijo": "fijo",
        "porcentaje": "porcentaje",
    }

    print("\nComo quieres ingresar el flete de importacion?")
    print("1. Valor fijo en la moneda original")
    print("2. Porcentaje sobre el precio del producto")

    while True:
        opcion = input(f"Modo de flete [1/2] ({valor_por_defecto}): ").strip().lower()
        if not opcion:
            return valor_por_defecto
        if opcion in equivalencias:
            return equivalencias[opcion]
        print("Opcion invalida. Elige 1 para fijo o 2 para porcentaje.")


def pedir_modo_flete_generico(mensaje: str, valor_por_defecto: str = "fijo") -> str:
    equivalencias = {
        "1": "fijo",
        "2": "porcentaje",
        "fijo": "fijo",
        "porcentaje": "porcentaje",
    }

    print(f"\n{mensaje}")
    print("1. Valor fijo")
    print("2. Porcentaje")

    while True:
        opcion = input(f"Modo de flete [1/2] ({valor_por_defecto}): ").strip().lower()
        if not opcion:
            return valor_por_defecto
        if opcion in equivalencias:
            return equivalencias[opcion]
        print("Opcion invalida. Elige 1 para fijo o 2 para porcentaje.")


def construir_importacion_desde_ultima(
    ultima: UltimaCotizacion | None,
    configuracion: Configuracion,
) -> CotizacionImportacionInput:
    valores = ultima.valores if ultima and ultima.tipo == "importacion" else {}
    flete_modo = pedir_modo_flete_importacion(str(valores.get("flete_modo", "fijo")).lower())
    mensaje_flete = "Flete en moneda original" if flete_modo == "fijo" else "Flete en porcentaje"

    return CotizacionImportacionInput(
        precio=pedir_float("Precio", float(valores.get("precio", 0)) or None),
        flete=pedir_float(mensaje_flete, float(valores.get("flete", 0)) or None),
        moneda=pedir_texto("Moneda (COP, USD o EUR)", str(valores.get("moneda", "USD"))).upper(),
        peso=pedir_float("Peso en kg", float(valores.get("peso", 0)) or None),
        ganancia_porcentaje=pedir_float(
            "Ganancia en porcentaje",
            float(valores.get("ganancia_porcentaje", configuracion.ganancia_importacion)),
        ),
        flete_modo=flete_modo,
    )


def construir_local_desde_ultima(
    ultima: UltimaCotizacion | None,
    configuracion: Configuracion,
) -> CotizacionLocalInput:
    valores = ultima.valores if ultima and ultima.tipo == "local" else {}
    flete_modo = pedir_modo_flete_generico(
        "Modo de flete local",
        str(valores.get("flete_modo", configuracion.flete_local_modo)).lower(),
    )
    return CotizacionLocalInput(
        precio_base_cop=pedir_float("Precio base en COP", float(valores.get("precio_base_cop", 0)) or None),
        flete_local=pedir_float(
            "Flete local",
            float(valores.get("flete_local", configuracion.flete_local)),
        ),
        ganancia_porcentaje=pedir_float(
            "Ganancia en porcentaje",
            float(valores.get("ganancia_porcentaje", configuracion.ganancia_local)),
        ),
        flete_modo=flete_modo,
    )


def construir_reparacion_desde_ultima(
    ultima: UltimaCotizacion | None,
    configuracion: Configuracion,
) -> CotizacionReparacionInput:
    valores = ultima.valores if ultima and ultima.tipo == "reparacion" else {}
    flete_modo = pedir_modo_flete_generico(
        "Modo de flete de reparacion",
        str(valores.get("flete_modo", configuracion.flete_reparacion_modo)).lower(),
    )
    return CotizacionReparacionInput(
        precio_base_usd=pedir_float("Precio base en USD", float(valores.get("precio_base_usd", 0)) or None),
        flete_reparacion=pedir_float(
            "Flete de reparacion",
            float(valores.get("flete_reparacion", configuracion.flete_reparacion)),
        ),
        ganancia_porcentaje=pedir_float(
            "Ganancia en porcentaje",
            float(valores.get("ganancia_porcentaje", configuracion.ganancia_reparacion)),
        ),
        peso=pedir_float("Peso en kg", float(valores.get("peso", 0)) or None),
        flete_modo=flete_modo,
    )


def ejecutar_cotizacion(tipo: str, ultima: UltimaCotizacion | None) -> None:
    configuracion = obtener_configuracion()

    if tipo == "importacion":
        entrada = construir_importacion_desde_ultima(ultima, configuracion)
        resultado = generar_cotizacion_importacion(entrada, configuracion, guardar_formulario=True)
        imprimir_resultado("COTIZACION DE IMPORTACION", resultado)
        return

    if tipo == "local":
        entrada = construir_local_desde_ultima(ultima, configuracion)
        resultado = generar_cotizacion_local(entrada, configuracion, guardar_formulario=True)
        imprimir_resultado("COTIZACION LOCAL", resultado)
        return

    entrada = construir_reparacion_desde_ultima(ultima, configuracion)
    resultado = generar_cotizacion_reparacion(entrada, configuracion, guardar_formulario=True)
    imprimir_resultado("COTIZACION DE REPARACION", resultado)


def main() -> None:
    ultima = obtener_ultima_cotizacion()

    print("COTIZADOR GOTRON")
    if ultima is not None:
        print(f"Ultima cotizacion guardada: {ultima.tipo} -> {ultima.valores}")

    usar_ultima = False
    tipo = pedir_tipo_cotizacion()
    if ultima is not None and ultima.tipo == tipo:
        usar_ultima = preguntar_si_no("Deseas reutilizar los valores de la ultima cotizacion", True)

    try:
        ejecutar_cotizacion(tipo, ultima if usar_ultima else None)
    except CotizadorError as error:
        print(f"\nError: {error}")


if __name__ == "__main__":
    main()
