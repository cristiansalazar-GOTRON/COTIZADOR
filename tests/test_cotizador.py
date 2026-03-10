import pytest

from cotizador import calculate_values, to_float


def test_to_float_accepts_comma_and_dot():
    assert to_float("1,23", "campo") == 1.23
    assert to_float("4.56", "campo") == 4.56


def test_to_float_raises_on_empty():
    with pytest.raises(ValueError) as exc:
        to_float("", "campo")
    assert "no puede estar vacio" in str(exc.value)


def test_to_float_invalid():
    with pytest.raises(ValueError):
        to_float("abc", "campo")


def make_data(**overrides):
    base = {
        "product_cost": 100.0,
        "freight_cost": 50.0,
        "currency": "USD",
        "usd_rate": 5000.0,
        "eur_rate": 6000.0,
        "threshold": 2000.0,
        "low_margin": 0.3,
        "high_margin": 0.5,
        "tariff_percent": 0.1,
        "vat_percent": 0.19,
    }
    base.update(overrides)
    return base


def test_calculate_low_margin_usd():
    data = make_data()
    result = calculate_values(data)
    assert result["margin"] == data["low_margin"]
    assert result["total_cost"] == 150.0
    assert result["cost_cop"] == 150.0 * 5000.0


def test_calculate_high_margin_exceeds_threshold():
    data = make_data(product_cost=2000, freight_cost=1000)
    result = calculate_values(data)
    assert result["margin"] == data["high_margin"]


def test_calculate_currency_eur():
    data = make_data(currency="EUR")
    result = calculate_values(data)
    assert result["cost_cop"] == data["total_cost"] * data["eur_rate"]


def test_all_returned_keys_present():
    data = make_data()
    result = calculate_values(data)
    expected_keys = {
        "total_cost",
        "cost_cop",
        "margin",
        "profit",
        "base_price",
        "tariff",
        "subtotal",
        "vat",
        "final_price",
    }
    assert expected_keys.issubset(result.keys())
