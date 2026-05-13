from __future__ import annotations

import random


def generate_lifestyle_sample() -> dict[str, int]:
    return {
        "daily_car_km": random.randint(0, 40),
        "daily_public_transport_km": random.randint(0, 30),
        "monthly_electricity_kwh": random.randint(80, 700),
        "meat_meals_per_week": random.randint(0, 14),
        "flights_per_year": random.randint(0, 12),
        "recycling_frequency": random.randint(0, 7),
    }


def generate_sample_set(count: int = 12) -> list[dict[str, int]]:
    return [generate_lifestyle_sample() for _ in range(count)]
