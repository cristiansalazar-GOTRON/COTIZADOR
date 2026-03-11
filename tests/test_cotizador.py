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
    # make_data doesn't include total_cost, so use returned value
    assert result["cost_cop"] == result["total_cost"] * data["eur_rate"]


def test_profit_and_final_price_are_positive():
    # additional sanity check to cover some of the new fields
    data = make_data()
    result = calculate_values(data)
    assert result["profit"] >= 0
    assert result["final_price"] >= result["cost_cop"]


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


def test_calculate_local_simple():
    # local calculations should only apply margin and vat
    from cotizador import calculate_local_values

    form = {
        "local_cost": 100000.0,
        "local_margin": 0.2,
        "local_vat": 0.1,
    }
    res = calculate_local_values(form)
    assert res["total_cost"] == 100000.0
    assert res["margin"] == 0.2
    assert res["profit"] == 20000.0
    assert res["base_price"] == 120000.0
    assert res["vat"] == 12000.0
    assert res["final_price"] == 132000.0


def test_calculate_values_with_cop_currency():
    # COP currency should use a rate of 1 and treat costs as already in COP
    data = make_data(currency="COP", usd_rate=0, eur_rate=0)
    data["product_cost"] = 100.0
    data["freight_cost"] = 50.0
    result = calculate_values(data)
    assert result["cost_cop"] == 150.0  # rate 1
    assert result["total_cost"] == 150.0
