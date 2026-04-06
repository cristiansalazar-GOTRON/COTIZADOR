from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class PasoCotizacion:
    descripcion: str
    valor: float
    moneda: str = "COP"


@dataclass(slots=True)
class ResultadoCotizacion:
    pasos: list[PasoCotizacion] = field(default_factory=list)
    total_final: float = 0.0

    def agregar_paso(self, descripcion: str, valor: float, moneda: str = "COP") -> None:
        self.pasos.append(PasoCotizacion(descripcion=descripcion, valor=valor, moneda=moneda))
        self.total_final = valor


@dataclass(slots=True)
class Configuracion:
    tasa_usd: float = 4200.0
    tasa_eur: float = 4500.0
    arancel_importacion: float = 10.0
    iva: float = 19.0
    ganancia_importacion: float = 30.0
    ganancia_local: float = 25.0
    ganancia_reparacion: float = 20.0
    flete_local: float = 12.0
    flete_local_modo: str = "porcentaje"
    flete_reparacion: float = 8.0
    flete_reparacion_modo: str = "porcentaje"
    recargo_valor_alto: float = 2_000_000.0
    recargo_peso: float = 350_000.0
    umbral_usd: float = 2000.0
    umbral_peso: float = 5.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CotizacionImportacionInput:
    precio: float
    flete: float
    moneda: str
    peso: float
    ganancia_porcentaje: float
    flete_modo: str = "fijo"


@dataclass(slots=True)
class CotizacionLocalInput:
    precio_base_cop: float
    flete_local: float
    ganancia_porcentaje: float
    flete_modo: str = "fijo"


@dataclass(slots=True)
class CotizacionReparacionInput:
    precio_base_usd: float
    flete_reparacion: float
    ganancia_porcentaje: float
    peso: float
    flete_modo: str = "porcentaje"


@dataclass(slots=True)
class UltimaCotizacion:
    tipo: str
    valores: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
