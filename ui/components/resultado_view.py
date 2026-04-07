from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget


class ResultadoView(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        pasos_card = QFrame()
        pasos_card.setObjectName("PanelCard")
        pasos_layout = QVBoxLayout(pasos_card)
        pasos_layout.setContentsMargins(5, 3, 5, 3)
        pasos_layout.setSpacing(0)

        pasos_titulo = QLabel("PASOS")
        pasos_titulo.setObjectName("CardTitle")
        pasos_layout.addWidget(pasos_titulo)

        pasos_grid = QGridLayout()
        pasos_grid.setContentsMargins(0, 0, 0, 0)
        pasos_grid.setHorizontalSpacing(8)
        pasos_grid.setVerticalSpacing(0)
        pasos_grid.setColumnMinimumWidth(0, 145)
        pasos_grid.setColumnStretch(0, 3)
        pasos_grid.setColumnStretch(1, 2)

        self.lbl_precio_valor = self._crear_fila_paso(
            pasos_grid, 0, "Precio producto:", destacado=False
        )
        self.lbl_flete_valor = self._crear_fila_paso(
            pasos_grid, 1, "Flete:", destacado=False
        )
        self.lbl_subtotal_valor = self._crear_fila_paso(
            pasos_grid, 2, "Subtotal:", destacado=False
        )
        self.lbl_conversion_valor = self._crear_fila_paso(
            pasos_grid, 3, "Conversión a COP:", destacado=False
        )
        self.lbl_ganancia_valor = self._crear_fila_paso(
            pasos_grid, 4, "Ganancia:", destacado=False
        )
        self.lbl_recargos_valor = self._crear_fila_paso(
            pasos_grid, 5, "Recargos:", destacado=False
        )
        self.lbl_subtotal_sin_iva_valor = self._crear_fila_paso(
            pasos_grid, 6, "Subtotal sin IVA:", destacado=False
        )
        self.lbl_iva_valor = self._crear_fila_paso(
            pasos_grid, 7, "IVA:", destacado=False
        )
        self.lbl_total_valor = self._crear_fila_paso(
            pasos_grid, 8, "TOTAL FINAL:", destacado=True
        )
        pasos_layout.addLayout(pasos_grid)
        layout.addWidget(pasos_card, 1)

    def limpiar(self) -> None:
        for label in self._labels_pasos():
            label.setText("-")

    def mostrar_resultado(
        self,
        tipo: str,
        moneda: str,
        ganancia: float,
        total_final: str,
        pasos: list[dict[str, str]],
    ) -> None:
        self._limpiar_pasos()
        self._mapear_pasos_backend(pasos)

    def _crear_fila_paso(
        self,
        layout: QGridLayout,
        fila: int,
        etiqueta: str,
        destacado: bool,
    ) -> QLabel:
        etiqueta_label = QLabel(etiqueta)
        etiqueta_label.setObjectName("PasoDescripcion")
        etiqueta_label.setWordWrap(True)
        etiqueta_label.setMinimumHeight(10)
        if destacado:
            etiqueta_label.setObjectName("PasoDescripcionTotal")

        valor_label = QLabel("-")
        valor_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        valor_label.setObjectName("PasoValor")
        valor_label.setMinimumHeight(10)
        if destacado:
            valor_label.setObjectName("PasoValorTotal")

        layout.addWidget(etiqueta_label, fila, 0)
        layout.addWidget(valor_label, fila, 1)
        return valor_label

    def _labels_pasos(self) -> list[QLabel]:
        return [
            self.lbl_precio_valor,
            self.lbl_flete_valor,
            self.lbl_subtotal_valor,
            self.lbl_conversion_valor,
            self.lbl_ganancia_valor,
            self.lbl_recargos_valor,
            self.lbl_subtotal_sin_iva_valor,
            self.lbl_iva_valor,
            self.lbl_total_valor,
        ]

    def _limpiar_pasos(self) -> None:
        for label in self._labels_pasos():
            label.setText("-")

    def _formatear_valor(self, valor: str, moneda: str) -> str:
        if valor in {"", "-"}:
            return "-"
        return f"{valor} {moneda}".strip()

    def _mapear_pasos_backend(self, pasos: list[dict[str, str]]) -> None:
        recargos_total = 0.0
        recargo_detectado = False

        for paso in pasos:
            descripcion = str(paso.get("descripcion", "")).lower()
            valor = str(paso.get("valor", "-"))
            moneda = str(paso.get("moneda", ""))

            if "precio" in descripcion:
                self.lbl_precio_valor.setText(self._formatear_valor(valor, moneda))
            elif "flete" in descripcion:
                self.lbl_flete_valor.setText(self._formatear_valor(valor, moneda))
            elif "subtotal en moneda original" in descripcion or "subtotal con flete local" in descripcion:
                self.lbl_subtotal_valor.setText(self._formatear_valor(valor, moneda))
            elif "subtotal con flete de reparacion" in descripcion:
                self.lbl_subtotal_valor.setText(self._formatear_valor(valor, moneda))
            elif "conversion" in descripcion:
                self.lbl_conversion_valor.setText(self._formatear_valor(valor, moneda))
            elif "ganancia" in descripcion:
                self.lbl_ganancia_valor.setText(self._formatear_valor(valor, moneda))
            elif "recargo" in descripcion:
                recargo_detectado = True
                try:
                    recargos_total += float(valor.replace(",", ""))
                except ValueError:
                    pass
            elif "subtotal antes de iva" in descripcion:
                self.lbl_subtotal_sin_iva_valor.setText(self._formatear_valor(valor, moneda))
            elif descripcion.strip() == "iva" or "valor del iva" in descripcion:
                self.lbl_iva_valor.setText(self._formatear_valor(valor, moneda))
            elif "total" in descripcion:
                self.lbl_total_valor.setText(self._formatear_valor(valor, moneda))

        if recargo_detectado:
            self.lbl_recargos_valor.setText(self._formatear_valor(f"{recargos_total:,.2f}", "COP"))
        else:
            self.lbl_recargos_valor.setText("0.00 COP")
