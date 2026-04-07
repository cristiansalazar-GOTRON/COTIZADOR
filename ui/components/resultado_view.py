from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget


PLANTILLAS_PASOS: dict[str, list[tuple[str, str, bool]]] = {
    "importacion": [
        ("Precio del producto", "Precio producto:", False),
        ("Calculo del flete", "Flete:", False),
        ("Subtotal en moneda original", "Subtotal:", False),
        ("Conversion a COP", "Conversion a COP:", False),
        ("Calculo de ganancia en COP", "Ganancia:", False),
        ("Recargo por valor alto", "Recargo por valor alto:", False),
        ("Recargo por peso", "Recargo por peso:", False),
        ("Subtotal antes de IVA", "Subtotal sin IVA:", False),
        ("IVA", "IVA:", False),
        ("Total final", "TOTAL FINAL:", True),
    ],
    "local": [
        ("Precio base en COP", "Precio base:", False),
        ("Subtotal con flete local", "Subtotal con flete:", False),
        ("Valor de la ganancia local en COP", "Ganancia:", False),
        ("Subtotal antes de IVA en COP", "Subtotal sin IVA:", False),
        ("Valor del IVA en COP", "IVA:", False),
        ("Total con IVA", "TOTAL FINAL:", True),
    ],
    "reparacion": [
        ("Precio del producto", "Precio producto:", False),
        ("Conversion a COP", "Conversion a COP:", False),
        ("Subtotal con flete de reparacion", "Subtotal con flete:", False),
        ("Valor de la ganancia de reparacion en COP", "Ganancia:", False),
        ("Recargo por valor alto", "Recargo por valor alto:", False),
        ("Recargo por peso", "Recargo por peso:", False),
        ("Subtotal antes de IVA", "Subtotal sin IVA:", False),
        ("IVA", "IVA:", False),
        ("Total final", "TOTAL FINAL:", True),
    ],
}


class PasoRow(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PasoRow")

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(0)
        layout.setColumnMinimumWidth(0, 160)
        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 2)

        self.etiqueta_label = QLabel("-")
        self.etiqueta_label.setObjectName("PasoDescripcion")
        self.etiqueta_label.setWordWrap(True)
        self.etiqueta_label.setMinimumHeight(10)
        self.etiqueta_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.valor_label = QLabel("-")
        self.valor_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.valor_label.setObjectName("PasoValor")
        self.valor_label.setMinimumHeight(10)
        self.valor_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout.addWidget(self.etiqueta_label, 0, 0)
        layout.addWidget(self.valor_label, 0, 1)

    def configurar(self, etiqueta: str, valor: str, destacado: bool) -> None:
        self.etiqueta_label.setText(etiqueta)
        self.valor_label.setText(valor)
        self.etiqueta_label.setObjectName("PasoDescripcionTotal" if destacado else "PasoDescripcion")
        self.valor_label.setObjectName("PasoValorTotal" if destacado else "PasoValor")
        self.style().unpolish(self.etiqueta_label)
        self.style().polish(self.etiqueta_label)
        self.style().unpolish(self.valor_label)
        self.style().polish(self.valor_label)


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
        pasos_titulo.setTextInteractionFlags(Qt.TextSelectableByMouse)
        pasos_layout.addWidget(pasos_titulo)

        self.rows_container = QVBoxLayout()
        self.rows_container.setContentsMargins(0, 0, 0, 0)
        self.rows_container.setSpacing(0)
        pasos_layout.addLayout(self.rows_container)

        self.paso_rows: list[PasoRow] = []
        for _ in range(10):
            row = PasoRow()
            self.paso_rows.append(row)
            self.rows_container.addWidget(row)

        layout.addWidget(pasos_card, 1)

    def limpiar(self) -> None:
        self._render_tipo("importacion", {})

    def mostrar_resultado(
        self,
        tipo: str,
        moneda: str,
        ganancia: float,
        total_final: str,
        pasos: list[dict[str, str]],
    ) -> None:
        del moneda, ganancia, total_final
        pasos_por_descripcion = {
            str(paso.get("descripcion", "")): self._formatear_valor(
                str(paso.get("valor", "-")),
                str(paso.get("moneda", "")),
            )
            for paso in pasos
        }
        self._render_tipo(tipo, pasos_por_descripcion)

    def _render_tipo(self, tipo: str, pasos_por_descripcion: dict[str, str]) -> None:
        plantilla = PLANTILLAS_PASOS[tipo]
        for index, row in enumerate(self.paso_rows):
            if index < len(plantilla):
                descripcion_backend, etiqueta, destacado = plantilla[index]
                valor = pasos_por_descripcion.get(descripcion_backend, "-")
                row.configurar(etiqueta, valor, destacado)
                row.show()
            else:
                row.hide()

    def _formatear_valor(self, valor: str, moneda: str) -> str:
        if valor in {"", "-"}:
            return "-"
        return f"{valor} {moneda}".strip()
