from __future__ import annotations


def km_to_miles(kilometers: float) -> float:
    return round(kilometers * 0.621371, 2)


def miles_to_km(miles: float) -> float:
    return round(miles / 0.621371, 2)


def annual_to_monthly(amount: float) -> float:
    return round(amount / 12, 2)


def kwh_to_co2(kwh: float, factor: float = 0.42) -> float:
    return round(kwh * factor, 2)
