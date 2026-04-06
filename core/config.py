from __future__ import annotations

import json
from pathlib import Path

from .modelos import Configuracion, UltimaCotizacion


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "data"
CONFIG_PATH = CONFIG_DIR / "configuracion.json"
LAST_QUOTE_PATH = CONFIG_DIR / "ultima_cotizacion.json"


def guardar_configuracion(configuracion: Configuracion, ruta: Path | None = None) -> Path:
    destino = ruta or CONFIG_PATH
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8") as archivo:
        json.dump(configuracion.to_dict(), archivo, indent=2, ensure_ascii=False)
    return destino


def cargar_configuracion(ruta: Path | None = None) -> Configuracion:
    origen = ruta or CONFIG_PATH
    if not origen.exists():
        configuracion = Configuracion()
        guardar_configuracion(configuracion, origen)
        return configuracion

    with origen.open("r", encoding="utf-8") as archivo:
        data = json.load(archivo)
    return Configuracion(**data)


def guardar_ultima_cotizacion(ultima_cotizacion: UltimaCotizacion, ruta: Path | None = None) -> Path:
    destino = ruta or LAST_QUOTE_PATH
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8") as archivo:
        json.dump(ultima_cotizacion.to_dict(), archivo, indent=2, ensure_ascii=False)
    return destino


def cargar_ultima_cotizacion(ruta: Path | None = None) -> UltimaCotizacion | None:
    origen = ruta or LAST_QUOTE_PATH
    if not origen.exists():
        return None

    with origen.open("r", encoding="utf-8") as archivo:
        data = json.load(archivo)
    return UltimaCotizacion(**data)
