from __future__ import annotations

from typing import Any

from .base_form import BaseCotizacionForm


class ReparacionForm(BaseCotizacionForm):
    titulo = "Datos de reparacion"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.precio_base = self.create_spinbox()
        self.moneda = self.create_combo(["COP", "USD", "EUR"])
        self.tasa_usd = self.create_spinbox()
        self.tasa_eur = self.create_spinbox()
        self.flete_reparacion = self.create_spinbox()
        self.flete_modo = self.create_combo(["fijo", "porcentaje"])
        self.ganancia = self.create_spinbox(suffix=" %")
        self.iva = self.create_spinbox(suffix=" %")
        self.peso = self.create_spinbox(step=0.1, suffix=" kg")

        self.add_field(0, "Precio base", self.precio_base, 0)
        self.add_field(0, "Moneda", self.moneda, 1)
        self.add_field(1, "Tasa USD", self.tasa_usd, 0)
        self.add_field(1, "Tasa EUR", self.tasa_eur, 1)
        self.add_field(2, "Flete rep.", self.flete_reparacion, 0)
        self.add_field(2, "Tipo flete", self.flete_modo, 1)
        self.add_field(3, "Ganancia", self.ganancia, 0)
        self.add_field(3, "IVA", self.iva, 1)
        self.add_field(4, "Peso", self.peso, 0)

        self.moneda.currentTextChanged.connect(self._toggle_rate_fields)
        self._toggle_rate_fields(self.moneda.currentText())

    def _toggle_rate_fields(self, moneda: str) -> None:
        self.tasa_usd.setEnabled(moneda in {"COP", "USD", "EUR"})
        self.tasa_eur.setEnabled(moneda == "EUR")

    def _populate(self, values: dict[str, Any]) -> None:
        self.precio_base.setValue(float(values.get("precio_base", 0)))
        self.moneda.setCurrentText(str(values.get("moneda", "USD")))
        self.tasa_usd.setValue(float(values.get("tasa_usd", 0) or 0))
        self.tasa_eur.setValue(float(values.get("tasa_eur", 0) or 0))
        self.flete_reparacion.setValue(float(values.get("flete_reparacion", 0)))
        self.flete_modo.setCurrentText(str(values.get("flete_modo", "fijo")))
        self.ganancia.setValue(float(values.get("ganancia_porcentaje", 0)))
        self.iva.setValue(float(values.get("iva_porcentaje", 0)))
        self.peso.setValue(float(values.get("peso", 0)))
        self._toggle_rate_fields(self.moneda.currentText())

    def reset(self) -> None:
        self.precio_base.setValue(0)
        self.moneda.setCurrentText("USD")
        self.tasa_usd.setValue(0)
        self.tasa_eur.setValue(0)
        self.flete_reparacion.setValue(0)
        self.flete_modo.setCurrentText("fijo")
        self.ganancia.setValue(0)
        self.iva.setValue(0)
        self.peso.setValue(0)
        self._toggle_rate_fields(self.moneda.currentText())

    def get_payload(self) -> dict[str, Any]:
        return {
            "precio_base": self.precio_base.value(),
            "moneda": self.moneda.currentText(),
            "tasa_usd": self.tasa_usd.value() or None,
            "tasa_eur": self.tasa_eur.value() or None,
            "flete_reparacion": self.flete_reparacion.value(),
            "flete_modo": self.flete_modo.currentText(),
            "ganancia_porcentaje": self.ganancia.value(),
            "iva_porcentaje": self.iva.value(),
            "peso": self.peso.value(),
        }
