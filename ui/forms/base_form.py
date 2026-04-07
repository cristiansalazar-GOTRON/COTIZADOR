from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class BaseCotizacionForm(QWidget):
    titulo = ""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        encabezado = QLabel(self.titulo)
        encabezado.setObjectName("FormTitle")

        card = QFrame()
        card.setObjectName("PanelCard")
        self.form_layout = QGridLayout(card)
        self.form_layout.setContentsMargins(14, 14, 14, 14)
        self.form_layout.setHorizontalSpacing(22)
        self.form_layout.setVerticalSpacing(10)
        self.form_layout.setColumnStretch(0, 1)
        self.form_layout.setColumnStretch(1, 1)
        self.form_layout.setColumnMinimumWidth(0, 250)
        self.form_layout.setColumnMinimumWidth(1, 250)
        self.form_layout.setAlignment(Qt.AlignTop)

        layout.addWidget(encabezado)
        layout.addWidget(card)

    def add_field(self, row: int, label: str, widget: QWidget, column_group: int = 0) -> None:
        base_col = 0 if column_group == 0 else 1
        field_container = QFrame()
        field_container.setObjectName("FieldBlock")
        field_layout = QVBoxLayout(field_container)
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(6)

        label_widget = QLabel(label)
        label_widget.setObjectName("FieldLabel")
        field_layout.addWidget(label_widget)
        field_layout.addWidget(widget)
        self.form_layout.addWidget(field_container, row, base_col)

    def create_spinbox(
        self,
        decimals: int = 2,
        maximum: float = 1_000_000_000,
        step: float = 1.0,
        suffix: str = "",
    ) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setDecimals(decimals)
        spin.setRange(0, maximum)
        spin.setSingleStep(step)
        spin.setSuffix(suffix)
        spin.setButtonSymbols(QDoubleSpinBox.NoButtons)
        spin.setMinimumHeight(30)
        spin.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        spin.setMaximumWidth(280)
        return spin

    def create_combo(self, values: list[str]) -> QComboBox:
        combo = QComboBox()
        combo.addItems(values)
        combo.setMinimumHeight(30)
        combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        combo.setMaximumWidth(280)
        return combo

    def populate(self, values: dict[str, Any] | None) -> None:
        if not values:
            self.reset()
            return
        self._populate(values)

    def _populate(self, values: dict[str, Any]) -> None:
        raise NotImplementedError

    def reset(self) -> None:
        raise NotImplementedError

    def get_payload(self) -> dict[str, Any]:
        raise NotImplementedError
