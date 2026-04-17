from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .components.resultado_view import ResultadoView
from .controller import CotizadorController
from .forms.importacion_form import ImportacionForm
from .forms.local_form import LocalForm
from .forms.reparacion_form import ReparacionForm


class GotronLogo(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(56, 56)

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        outer_pen = QPen(QColor("#7DD3FC"), 8)
        outer_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(outer_pen)
        painter.drawArc(8, 8, 40, 40, 35 * 16, 280 * 16)

        inner_pen = QPen(QColor("#1D4ED8"), 8)
        inner_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(inner_pen)
        painter.drawArc(13, 13, 30, 30, 215 * 16, 270 * 16)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#94A3B8"))
        painter.drawEllipse(24, 24, 8, 8)

        painter.setBrush(QColor("#38BDF8"))
        painter.drawEllipse(38, 6, 6, 6)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.controller = CotizadorController()
        self.setWindowTitle("Cotizador GOTRON")
        self.resize(860, 760)
        self.setMinimumSize(820, 760)

        central = QWidget()
        self.setCentralWidget(central)
        self.root_layout = QVBoxLayout(central)
        self.root_layout.setContentsMargins(10, 10, 10, 10)
        self.root_layout.setSpacing(8)
        self.root_layout.setAlignment(Qt.AlignTop)

        body_layout = QGridLayout()
        body_layout.setHorizontalSpacing(10)
        body_layout.setVerticalSpacing(2)
        body_layout.setColumnStretch(0, 1)
        body_layout.setColumnStretch(1, 1)
        body_layout.setColumnMinimumWidth(0, 0)
        body_layout.setColumnMinimumWidth(1, 0)
        body_layout.setRowStretch(0, 0)
        body_layout.setAlignment(Qt.AlignTop)

        self.sidebar = self._build_sidebar()
        self.form_panel = self._build_form_panel()
        self.resultado_panel = self._build_result_panel()

        body_layout.addWidget(self.sidebar, 0, 0, alignment=Qt.AlignTop)
        body_layout.addWidget(self.form_panel, 0, 1, alignment=Qt.AlignTop)
        body_layout.addWidget(self.resultado_panel, 1, 0, 1, 2, alignment=Qt.AlignTop)
        body_layout.setRowStretch(0, 0)
        body_layout.setRowStretch(1, 1)

        self.root_layout.addLayout(body_layout, 1)

        self._apply_styles()
        self._load_initial_state(usar_ultima=False)
        self._sync_top_panel_heights()
        self.adjustSize()

    def _build_sidebar(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("SidebarCard")
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        frame.setMinimumHeight(392)
        frame.setMinimumWidth(0)
        frame.setMaximumWidth(16777215)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        branding_row = QHBoxLayout()
        branding_row.setContentsMargins(0, 0, 0, 0)
        branding_row.setSpacing(10)

        logo = GotronLogo()
        brand = QLabel("Cotizador GOTRON")
        brand.setObjectName("BrandTitle")
        brand.setTextInteractionFlags(Qt.TextSelectableByMouse)
        tagline = QLabel("Panel tecnico claro y rapido.")
        tagline.setWordWrap(True)
        tagline.setObjectName("SidebarText")
        tagline.setTextInteractionFlags(Qt.TextSelectableByMouse)

        brand_block = QVBoxLayout()
        brand_block.setContentsMargins(0, 0, 0, 0)
        brand_block.setSpacing(2)
        brand_block.addWidget(brand)
        brand_block.addWidget(tagline)

        branding_row.addWidget(logo, 0, Qt.AlignTop)
        branding_row.addLayout(brand_block, 1)

        tipo_label = QLabel("Tipo de cotizacion")
        tipo_label.setObjectName("SidebarSection")
        tipo_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.tipo_selector = QComboBox()
        self.tipo_selector.addItem("Importacion", "importacion")
        self.tipo_selector.addItem("Local", "local")
        self.tipo_selector.addItem("Reparacion", "reparacion")

        self.btn_nueva = QPushButton("Nueva cotizacion")
        self.btn_ultima = QPushButton("Usar ultima cotizacion")
        self.btn_calcular = QPushButton("Calcular cotizacion")
        self.btn_calcular.setObjectName("PrimaryButton")

        self.tipo_actual = QLabel("Actual: Importacion")
        self.tipo_actual.setObjectName("SidebarTextStrong")
        self.tipo_actual.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.ultima_info = QLabel("Ultima: sin registro")
        self.ultima_info.setWordWrap(True)
        self.ultima_info.setObjectName("SidebarText")
        self.ultima_info.setMaximumHeight(42)
        self.ultima_info.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout.addLayout(branding_row)
        layout.addWidget(tipo_label)
        layout.addWidget(self.tipo_selector)
        layout.addWidget(self.btn_nueva)
        layout.addWidget(self.btn_ultima)
        layout.addWidget(self.btn_calcular)
        layout.addSpacing(0)
        layout.addWidget(self.tipo_actual)
        layout.addWidget(self.ultima_info)
        layout.addStretch(1)

        self.tipo_selector.currentIndexChanged.connect(self._on_type_changed)
        self.btn_nueva.clicked.connect(lambda: self._load_initial_state(usar_ultima=False))
        self.btn_ultima.clicked.connect(lambda: self._load_initial_state(usar_ultima=True))
        self.btn_calcular.clicked.connect(self._calcular)
        return frame

    def _build_form_panel(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("PanelCard")
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        frame.setMinimumHeight(392)
        frame.setMinimumWidth(0)
        frame.setMaximumWidth(16777215)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        titulo = QLabel("Datos de cotizacion")
        titulo.setObjectName("PanelTitle")
        titulo.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.stacked_forms = QStackedWidget()
        self.importacion_form = ImportacionForm()
        self.local_form = LocalForm()
        self.reparacion_form = ReparacionForm()

        self.stacked_forms.addWidget(self.importacion_form)
        self.stacked_forms.addWidget(self.local_form)
        self.stacked_forms.addWidget(self.reparacion_form)
        self.stacked_forms.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.stacked_forms.setMinimumHeight(330)

        layout.addWidget(titulo)
        layout.addWidget(self.stacked_forms, 0, Qt.AlignTop)
        return frame

    def _build_result_panel(self) -> QFrame:
        self.resultado_view = ResultadoView()
        frame = QFrame()
        frame.setObjectName("ResultWrapper")
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.resultado_view)
        return frame

    def _current_form(self):
        tipo = self._current_type()
        if tipo == "importacion":
            return self.importacion_form
        if tipo == "local":
            return self.local_form
        return self.reparacion_form

    def _current_type(self) -> str:
        return str(self.tipo_selector.currentData() or "importacion")

    def _current_type_index(self) -> int:
        tipo = self._current_type()
        mapping = {"importacion": 0, "local": 1, "reparacion": 2}
        return mapping[tipo]

    def _load_initial_state(self, usar_ultima: bool) -> None:
        tipo = self._current_type()
        valores = self.controller.obtener_valores_iniciales(tipo, usar_ultima)
        self._current_form().populate(valores)
        self._refresh_sidebar_info()
        self.resultado_view.limpiar()
        self._sync_top_panel_heights()

    def _refresh_sidebar_info(self) -> None:
        tipo = self._current_type()
        self.tipo_actual.setText(f"Actual: {tipo.title()}")
        ultima = self.controller.obtener_ultima_cotizacion_info()
        if not ultima:
            self.ultima_info.setText("Ultima: sin registro")
            return

        valores = ultima["valores"]
        moneda = valores.get("moneda", "COP")
        precio = (
            valores.get("precio")
            or valores.get("precio_base")
            or valores.get("precio_base_cop")
            or 0
        )
        self.ultima_info.setText(
            f"Ultima {ultima['tipo'].title()} | {moneda} | {precio}"
        )

    def _on_type_changed(self, _: int) -> None:
        self.stacked_forms.setCurrentIndex(self._current_type_index())
        self._load_initial_state(usar_ultima=False)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._sync_top_panel_heights()

    def _sync_top_panel_heights(self) -> None:
        target_height = max(self.sidebar.sizeHint().height(), self.form_panel.sizeHint().height(), 392)
        self.sidebar.setFixedHeight(target_height)
        self.form_panel.setFixedHeight(target_height)

    def _calcular(self) -> None:
        tipo = self._current_type()
        form = self._current_form()
        payload = form.get_payload()
        try:
            self.controller.validar_payload(payload)
            self.btn_calcular.setText("Calculando...")
            QApplication.processEvents()
            resultado = self.controller.calcular(tipo, payload)
            self.resultado_view.mostrar_resultado(
                tipo=resultado["tipo"],
                moneda=resultado["moneda"],
                ganancia=resultado["ganancia"],
                total_final=resultado["total_final"],
                pasos=resultado["pasos"],
            )
            self._refresh_sidebar_info()
        except Exception as error:
            QMessageBox.critical(self, "Error de validacion", str(error))
        finally:
            self.btn_calcular.setText("Calcular cotizacion")

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background-color: #F4F6F8;
                color: #13263a;
                font-family: "Segoe UI Variable";
                font-size: 12px;
            }
            QLabel {
                background: transparent;
            }
            QMainWindow {
                background-color: #F4F6F8;
            }
            QLabel#BrandTitle {
                font-size: 20px;
                font-weight: 700;
                color: #1D4ED8;
            }
            QLabel#PanelTitle, QLabel#CardTitle, QLabel#SidebarSection, QLabel#FormTitle {
                font-size: 13px;
                font-weight: 700;
                color: #0F172A;
            }
            QLabel#SidebarText {
                color: #64748B;
                font-size: 11px;
            }
            QLabel#SidebarTextStrong {
                color: #1E293B;
                font-weight: 600;
                font-size: 11px;
            }
            QLabel#ResumenInline {
                color: #334155;
                font-size: 12px;
                font-weight: 600;
            }
            QLabel#TotalLabel {
                color: #1D4ED8;
                font-size: 18px;
                font-weight: 700;
            }
            QFrame#SidebarCard, QFrame#PanelCard, QFrame#TotalCard {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 18px;
            }
            QFrame#FieldBlock {
                background: transparent;
                border: none;
            }
            QFrame#PasoRow {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
            QFrame#ResultWrapper {
                background: transparent;
            }
            QComboBox, QDoubleSpinBox, QPushButton {
                min-height: 30px;
                border-radius: 10px;
                border: 1px solid #AFC4DD;
                background-color: #FFFFFF;
                padding: 2px 7px;
            }
            QComboBox:hover, QDoubleSpinBox:hover, QPushButton:hover {
                border-color: #60A5FA;
            }
            QComboBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #3A7AFE;
                background-color: #F5FAFF;
            }
            QComboBox, QDoubleSpinBox {
                color: #0F172A;
                font-size: 10px;
                font-weight: 500;
            }
            QComboBox {
                padding-right: 28px;
            }
            QComboBox::drop-down {
                border: none;
                width: 26px;
                subcontrol-origin: padding;
                subcontrol-position: top right;
            }
            QComboBox::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #64748B;
                margin-right: 10px;
            }
            QPushButton {
                background-color: #FFFFFF;
                color: #0F172A;
                font-weight: 600;
                margin: 1px 0;
            }
            QPushButton#PrimaryButton {
                background-color: #3A7AFE;
                color: white;
                font-weight: 700;
            }
            QPushButton#PrimaryButton:hover {
                background-color: #2563EB;
            }
            QPushButton#PrimaryButton:pressed {
                background-color: #1D4ED8;
            }
            QLabel#FieldLabel {
                color: #334155;
                font-size: 12px;
                font-weight: 600;
                padding-left: 2px;
            }
            QLabel#PasoDescripcion {
                color: #334155;
                font-size: 14px;
                font-weight: 600;
            }
            QLabel#PasoDescripcionTotal {
                color: #0F172A;
                font-size: 15px;
                font-weight: 700;
            }
            QLabel#PasoValor {
                color: #0F172A;
                font-size: 14px;
                font-weight: 700;
            }
            QLabel#PasoValorTotal {
                color: #1D4ED8;
                font-size: 16px;
                font-weight: 800;
            }
            QLabel#PasoMoneda {
                color: #1D4ED8;
                font-size: 11px;
                font-weight: 700;
                background-color: #EFF6FF;
                border-radius: 10px;
                padding: 4px 8px;
            }
            QLabel#PasoEmpty {
                color: #94A3B8;
                font-size: 12px;
                padding: 24px;
                border: 1px dashed #CBD5E1;
                border-radius: 14px;
                background-color: #F8FAFC;
            }
            """
        )
