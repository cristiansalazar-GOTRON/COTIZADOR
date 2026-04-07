from __future__ import annotations

from typing import Any

from core.servicios import (
    generar_cotizacion_importacion_desde_payload,
    generar_cotizacion_local_desde_payload,
    generar_cotizacion_reparacion_desde_payload,
    obtener_configuracion,
    obtener_ultima_cotizacion,
)
from core.utils import ValidacionError


SECUENCIAS_PASOS: dict[str, list[str]] = {
    "importacion": [
        "Precio del producto",
        "Calculo del flete",
        "Subtotal en moneda original",
        "Conversion a COP",
        "Calculo de ganancia en COP",
        "Recargo por valor alto",
        "Recargo por peso",
        "Subtotal antes de IVA",
        "IVA",
        "Total final",
    ],
    "local": [
        "Precio base en COP",
        "Subtotal con flete local",
        "Valor de la ganancia local en COP",
        "Subtotal antes de IVA en COP",
        "Valor del IVA en COP",
        "Total con IVA",
    ],
    "reparacion": [
        "Precio del producto",
        "Conversion a COP",
        "Subtotal con flete de reparacion",
        "Valor de la ganancia de reparacion en COP",
        "Recargo por valor alto",
        "Recargo por peso",
        "Subtotal antes de IVA",
        "IVA",
        "Total final",
    ],
}


class CotizadorController:
    def __init__(self) -> None:
        self.configuracion = obtener_configuracion()

    def refrescar_configuracion(self) -> None:
        self.configuracion = obtener_configuracion()

    def obtener_ultima_cotizacion_info(self) -> dict[str, Any] | None:
        ultima = obtener_ultima_cotizacion()
        if ultima is None:
            return None
        return {"tipo": ultima.tipo, "valores": ultima.valores}

    def nueva_cotizacion(self) -> None:
        self.refrescar_configuracion()

    def construir_por_defecto(self, tipo: str) -> dict[str, Any]:
        config = self.configuracion
        if tipo == "importacion":
            return {
                "moneda": "USD",
                "flete_modo": "fijo",
                "ganancia_porcentaje": config.ganancia_importacion,
                "iva_porcentaje": config.iva,
                "tasa_usd": config.tasa_usd,
                "tasa_eur": config.tasa_eur,
            }
        if tipo == "local":
            return {
                "flete_local": config.flete_local,
                "flete_modo": config.flete_local_modo,
                "ganancia_porcentaje": config.ganancia_local,
                "iva_porcentaje": config.iva,
            }
        return {
            "moneda": "USD",
            "flete_reparacion": config.flete_reparacion,
            "flete_modo": config.flete_reparacion_modo,
            "ganancia_porcentaje": config.ganancia_reparacion,
            "iva_porcentaje": config.iva,
            "tasa_usd": config.tasa_usd,
            "tasa_eur": config.tasa_eur,
        }

    def obtener_valores_iniciales(self, tipo: str, usar_ultima: bool) -> dict[str, Any]:
        defaults = self.construir_por_defecto(tipo)
        if not usar_ultima:
            return defaults
        ultima = self.obtener_ultima_cotizacion_info()
        if not ultima or ultima["tipo"] != tipo:
            return defaults
        defaults.update(ultima["valores"])
        return defaults

    def calcular(self, tipo: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.refrescar_configuracion()
        if tipo == "importacion":
            resultado = generar_cotizacion_importacion_desde_payload(
                payload,
                self.configuracion,
                guardar_formulario=True,
            )
            moneda = payload["moneda"]
        elif tipo == "local":
            resultado = generar_cotizacion_local_desde_payload(
                payload,
                self.configuracion,
                guardar_formulario=True,
            )
            moneda = "COP"
        else:
            resultado = generar_cotizacion_reparacion_desde_payload(
                payload,
                self.configuracion,
                guardar_formulario=True,
            )
            moneda = payload["moneda"]

        pasos = self._normalizar_pasos(tipo, payload, resultado.pasos)
        return {
            "tipo": tipo,
            "moneda": moneda,
            "ganancia": payload["ganancia_porcentaje"],
            "total_final": f"COP {resultado.total_final:,.2f}",
            "pasos": pasos,
        }

    def validar_payload(self, payload: dict[str, Any]) -> None:
        for clave, valor in payload.items():
            if valor is None:
                continue
            if isinstance(valor, float) and valor < 0:
                raise ValidacionError(f"El valor '{clave}' no puede ser negativo.")

    def _normalizar_pasos(
        self,
        tipo: str,
        payload: dict[str, Any],
        pasos_backend: list[Any],
    ) -> list[dict[str, str]]:
        pasos_por_nombre = {
            paso.descripcion: {
                "descripcion": paso.descripcion,
                "valor": f"{paso.valor:,.2f}",
                "moneda": paso.moneda,
            }
            for paso in pasos_backend
        }
        secuencia = SECUENCIAS_PASOS[tipo]
        moneda_original = payload.get("moneda", "COP")
        pasos_normalizados: list[dict[str, str]] = []

        for descripcion in secuencia:
            paso = pasos_por_nombre.get(descripcion)
            if paso is None:
                pasos_normalizados.append(
                    {
                        "descripcion": descripcion,
                        "valor": "0.00",
                        "moneda": self._moneda_por_defecto(tipo, descripcion, moneda_original),
                    }
                )
            else:
                pasos_normalizados.append(paso)
        return pasos_normalizados

    def _moneda_por_defecto(self, tipo: str, descripcion: str, moneda_original: str) -> str:
        if tipo == "importacion" and descripcion in {
            "Precio del producto",
            "Calculo del flete",
            "Subtotal en moneda original",
        }:
            return moneda_original
        if tipo == "reparacion" and descripcion == "Precio del producto":
            return moneda_original
        return "COP"
