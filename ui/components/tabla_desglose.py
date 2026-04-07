from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class PasoRow(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PasoRow")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        self.descripcion_label = QLabel("-")
        self.descripcion_label.setObjectName("PasoDescripcion")
        self.valor_label = QLabel("0.00")
        self.valor_label.setObjectName("PasoValor")
        self.valor_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.moneda_label = QLabel("COP")
        self.moneda_label.setObjectName("PasoMoneda")
        self.moneda_label.setAlignment(Qt.AlignCenter)
        self.moneda_label.setFixedWidth(52)

        layout.addWidget(self.descripcion_label, 1)
        layout.addWidget(self.valor_label, 0)
        layout.addWidget(self.moneda_label, 0)

    def set_data(self, descripcion: str, valor: str, moneda: str) -> None:
        self.descripcion_label.setText(descripcion)
        self.valor_label.setText(valor)
        self.moneda_label.setText(moneda)


class TablaDesglose(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)

        self.empty_label = QLabel("Los pasos del calculo apareceran aqui.")
        self.empty_label.setObjectName("PasoEmpty")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.empty_label)

    def limpiar(self) -> None:
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.empty_label = QLabel("Los pasos del calculo apareceran aqui.")
        self.empty_label.setObjectName("PasoEmpty")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.empty_label)

    def cargar_pasos(self, pasos: list[dict[str, str]]) -> None:
        self.limpiar()
        if not pasos:
            return

        self.empty_label.deleteLater()
        self.empty_label = None

        for paso in pasos:
            row = PasoRow()
            row.set_data(
                str(paso["descripcion"]),
                str(paso["valor"]),
                str(paso["moneda"]),
            )
            self.layout.addWidget(row)
        self.layout.addStretch(1)
