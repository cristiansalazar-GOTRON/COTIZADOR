from pathlib import Path

import pytest

from core.calculos import cotizacion_importacion, cotizacion_local, cotizacion_reparacion
from core.config import (
    cargar_configuracion,
    cargar_ultima_cotizacion,
    guardar_configuracion,
    guardar_ultima_cotizacion,
)
from core.modelos import (
    Configuracion,
    CotizacionImportacionInput,
    CotizacionLocalInput,
    CotizacionReparacionInput,
    UltimaCotizacion,
)
from core.servicios import generar_cotizacion_importacion
from core.utils import ValidacionError, aplicar_porcentaje, convertir_a_cop


def test_convertir_a_cop_usd():
    assert convertir_a_cop(100, "USD", 4200, 4500) == 420000


def test_convertir_a_cop_cop():
    assert convertir_a_cop(100, "COP", 4200, 4500) == 100


def test_aplicar_porcentaje():
    assert aplicar_porcentaje(1000, 19) == 190


def test_cotizacion_importacion_con_recargos():
    configuracion = Configuracion(
        tasa_usd=4000,
        tasa_eur=4500,
        iva=19,
        ganancia_importacion=20,
        ganancia_local=25,
        ganancia_reparacion=15,
        flete_local=12,
        flete_reparacion=8,
        recargo_valor_alto=2_000_000,
        recargo_peso=300_000,
        umbral_usd=2000,
        umbral_peso=5,
    )

    resultado = cotizacion_importacion(
        CotizacionImportacionInput(
            precio=2500,
            flete=200,
            moneda="USD",
            peso=6,
            ganancia_porcentaje=20,
            flete_modo="fijo",
        ),
        configuracion,
    )

    assert resultado.total_final == pytest.approx(18_159_400)
    assert [paso.descripcion for paso in resultado.pasos] == [
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
    ]
    assert resultado.pasos[0].moneda == "USD"
    assert resultado.pasos[1].moneda == "USD"
    assert resultado.pasos[2].moneda == "USD"
    assert resultado.pasos[3].moneda == "COP"


def test_cotizacion_importacion_con_flete_porcentaje():
    configuracion = Configuracion(
        tasa_usd=4000,
        tasa_eur=4500,
        iva=19,
        ganancia_importacion=20,
        recargo_valor_alto=2_000_000,
        recargo_peso=300_000,
        umbral_usd=2000,
        umbral_peso=5,
    )

    resultado = cotizacion_importacion(
        CotizacionImportacionInput(
            precio=1000,
            flete=10,
            moneda="USD",
            peso=2,
            ganancia_porcentaje=20,
            flete_modo="porcentaje",
        ),
        configuracion,
    )

    assert resultado.pasos[1].descripcion == "Calculo del flete"
    assert resultado.pasos[1].valor == pytest.approx(100)
    assert resultado.total_final == pytest.approx(6_283_200)


def test_cotizacion_local_con_flete_porcentaje():
    configuracion = Configuracion(iva=19)

    resultado = cotizacion_local(
        CotizacionLocalInput(
            precio_base_cop=1_000_000,
            flete_local=10,
            ganancia_porcentaje=20,
            flete_modo="porcentaje",
        ),
        configuracion,
    )

    assert resultado.total_final == pytest.approx(1_570_800)
    assert all(paso.moneda == "COP" for paso in resultado.pasos)


def test_cotizacion_local_con_flete_fijo():
    configuracion = Configuracion(iva=19)

    resultado = cotizacion_local(
        CotizacionLocalInput(
            precio_base_cop=1_000_000,
            flete_local=120_000,
            ganancia_porcentaje=20,
            flete_modo="fijo",
        ),
        configuracion,
    )

    assert resultado.total_final == pytest.approx(1_599_360)


def test_cotizacion_reparacion_sin_recargos():
    configuracion = Configuracion(
        tasa_usd=4000,
        iva=19,
        umbral_usd=2000,
        umbral_peso=5,
    )

    resultado = cotizacion_reparacion(
        CotizacionReparacionInput(
            precio_base_usd=500,
            flete_reparacion=10,
            ganancia_porcentaje=20,
            peso=3,
            flete_modo="porcentaje",
        ),
        configuracion,
    )

    assert resultado.total_final == pytest.approx(3_141_600)


def test_no_permite_valores_negativos():
    with pytest.raises(ValidacionError):
        cotizacion_local(
            CotizacionLocalInput(precio_base_cop=-1, flete_local=0, ganancia_porcentaje=20),
            Configuracion(),
        )


def test_valida_moneda():
    with pytest.raises(ValidacionError):
        cotizacion_importacion(
            CotizacionImportacionInput(
                precio=100,
                flete=10,
                moneda="XXX",
                peso=1,
                ganancia_porcentaje=10,
                flete_modo="fijo",
            ),
            Configuracion(),
        )


def test_valida_modo_flete_importacion():
    with pytest.raises(ValidacionError):
        cotizacion_importacion(
            CotizacionImportacionInput(
                precio=100,
                flete=10,
                moneda="USD",
                peso=1,
                ganancia_porcentaje=10,
                flete_modo="automatico",
            ),
            Configuracion(),
        )


def test_valida_modo_flete_local():
    with pytest.raises(ValidacionError):
        cotizacion_local(
            CotizacionLocalInput(
                precio_base_cop=1000,
                flete_local=100,
                ganancia_porcentaje=20,
                flete_modo="automatico",
            ),
            Configuracion(),
        )


def test_crea_configuracion_por_defecto_si_no_existe(tmp_path: Path):
    ruta = tmp_path / "configuracion.json"

    configuracion = cargar_configuracion(ruta)

    assert ruta.exists()
    assert isinstance(configuracion, Configuracion)


def test_guarda_y_carga_configuracion(tmp_path: Path):
    ruta = tmp_path / "configuracion.json"
    configuracion = Configuracion(tasa_usd=5000, ganancia_local=35, flete_local_modo="fijo")

    guardar_configuracion(configuracion, ruta)
    recargada = cargar_configuracion(ruta)

    assert recargada.tasa_usd == 5000
    assert recargada.ganancia_local == 35
    assert recargada.flete_local_modo == "fijo"


def test_guarda_y_carga_ultima_cotizacion(tmp_path: Path):
    ruta = tmp_path / "ultima_cotizacion.json"
    ultima = UltimaCotizacion(
        tipo="importacion",
        valores={
            "precio": 1500,
            "flete": 80,
            "moneda": "USD",
            "peso": 2.5,
            "ganancia_porcentaje": 30,
            "flete_modo": "fijo",
        },
    )

    guardar_ultima_cotizacion(ultima, ruta)
    recargada = cargar_ultima_cotizacion(ruta)

    assert recargada is not None
    assert recargada.tipo == "importacion"
    assert recargada.valores["moneda"] == "USD"
    assert recargada.valores["flete_modo"] == "fijo"


def test_servicio_guarda_formulario_de_la_ultima_cotizacion(tmp_path: Path):
    ruta = tmp_path / "ultima_cotizacion.json"
    entrada = CotizacionImportacionInput(
        precio=1000,
        flete=100,
        moneda="USD",
        peso=4,
        ganancia_porcentaje=25,
        flete_modo="fijo",
    )

    from core import servicios as servicios_modulo

    original = servicios_modulo.guardar_ultima_cotizacion
    servicios_modulo.guardar_ultima_cotizacion = lambda ultima_cotizacion: guardar_ultima_cotizacion(
        ultima_cotizacion,
        ruta,
    )
    try:
        generar_cotizacion_importacion(entrada, Configuracion(), guardar_formulario=True)
    finally:
        servicios_modulo.guardar_ultima_cotizacion = original

    recargada = cargar_ultima_cotizacion(ruta)
    assert recargada is not None
    assert recargada.tipo == "importacion"
    assert recargada.valores["flete"] == 100
    assert recargada.valores["flete_modo"] == "fijo"


def test_importacion_acepta_moneda_cop():
    configuracion = Configuracion(iva=19)
    resultado = cotizacion_importacion(
        CotizacionImportacionInput(
            precio=1_000_000,
            flete=100_000,
            moneda="COP",
            peso=2,
            ganancia_porcentaje=10,
            flete_modo="fijo",
        ),
        configuracion,
    )

    assert resultado.pasos[0].moneda == "COP"
    assert resultado.total_final == pytest.approx(1_439_900)
