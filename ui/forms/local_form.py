from __future__ import annotations

from typing import Any

from .base_form import BaseCotizacionForm


class LocalForm(BaseCotizacionForm):
    titulo = "Datos de venta local"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.precio_base = self.create_spinbox()
        self.flete_local = self.create_spinbox()
        self.flete_modo = self.create_combo(["fijo", "porcentaje"])
        self.ganancia = self.create_spinbox(suffix=" %")
        self.iva = self.create_spinbox(suffix=" %")

        self.add_field(0, "Precio base", self.precio_base, 0)
        self.add_field(0, "Flete local", self.flete_local, 1)
        self.add_field(1, "Tipo flete", self.flete_modo, 0)
        self.add_field(1, "Ganancia", self.ganancia, 1)
        self.add_field(2, "IVA", self.iva, 0)

    def _populate(self, values: dict[str, Any]) -> None:
        self.precio_base.setValue(float(values.get("precio_base_cop", 0)))
        self.flete_local.setValue(float(values.get("flete_local", 0)))
        self.flete_modo.setCurrentText(str(values.get("flete_modo", "fijo")))
        self.ganancia.setValue(float(values.get("ganancia_porcentaje", 0)))
        self.iva.setValue(float(values.get("iva_porcentaje", 0)))

    def reset(self) -> None:
        self.precio_base.setValue(0)
        self.flete_local.setValue(0)
        self.flete_modo.setCurrentText("fijo")
        self.ganancia.setValue(0)
        self.iva.setValue(0)

    def get_payload(self) -> dict[str, Any]:
        return {
            "precio_base_cop": self.precio_base.value(),
            "flete_local": self.flete_local.value(),
            "flete_modo": self.flete_modo.currentText(),
            "ganancia_porcentaje": self.ganancia.value(),
            "iva_porcentaje": self.iva.value(),
        }
