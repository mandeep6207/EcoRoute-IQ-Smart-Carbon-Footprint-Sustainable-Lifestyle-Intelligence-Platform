from __future__ import annotations

from typing import Dict

from utils.conversions import annual_to_monthly, kwh_to_co2, km_to_miles


def clamp(value: float, minimum: float = 0, maximum: float = 100) -> float:
    return max(minimum, min(maximum, value))


def sustainability_rating(score: float) -> str:
    if score <= 30:
        return "Eco Friendly"
    if score <= 70:
        return "Moderate Impact"
    return "High Impact"


def to_float(payload: Dict[str, float], key: str) -> float:
    return float(payload.get(key, 0) or 0)


def calculate_emissions(daily_car: float, daily_public: float, electricity: float, meat: float, flights: float, recycling: float) -> Dict[str, float]:
    transport_emissions = (km_to_miles(daily_car) * 30 * 0.192) + (km_to_miles(daily_public) * 30 * 0.055)
    home_emissions = kwh_to_co2(electricity)
    diet_emissions = meat * 4.33 * 2.3
    travel_emissions = annual_to_monthly(flights * 230)
    recycling_credit = recycling * 1.2

    return {
        "transport_emissions": round(transport_emissions, 2),
        "home_emissions": round(home_emissions, 2),
        "diet_emissions": round(diet_emissions, 2),
        "travel_emissions": round(travel_emissions, 2),
        "recycling_credit": round(recycling_credit, 2),
    }


def calculate_score(daily_car: float, daily_public: float, electricity: float, meat: float, flights: float, recycling: float) -> float:
    raw_score = (
        daily_car * 0.8
        + daily_public * 0.25
        + electricity * 0.08
        + meat * 2.5
        + flights * 8.0
        - (recycling * 1.5)
    )
    return clamp(round(raw_score, 0))


def build_category_breakdown(emissions: Dict[str, float]) -> Dict[str, float]:
    return {
        "Transport": emissions["transport_emissions"],
        "Home energy": emissions["home_emissions"],
        "Diet": emissions["diet_emissions"],
        "Flights": emissions["travel_emissions"],
        "Recycling credit": round(-emissions["recycling_credit"], 2),
    }


def build_source_scores(daily_car: float, daily_public: float, electricity: float, meat: float, flights: float, recycling: float) -> Dict[str, float]:
    return {
        "Car travel": round(daily_car * 0.8, 2),
        "Public transport": round(daily_public * 0.25, 2),
        "Electricity": round(electricity * 0.08, 2),
        "Food habits": round(meat * 2.5, 2),
        "Flights": round(flights * 8.0, 2),
        "Recycling": round(max(0.0, 15.0 - recycling * 1.5), 2),
    }


def build_reduction_opportunities(daily_car: float, electricity: float, meat: float, flights: float, recycling: float) -> list[dict[str, float | str]]:
    return [
        {"label": "Car travel", "impact": round(min(100.0, daily_car * 4.0), 1)},
        {"label": "Electricity", "impact": round(min(100.0, electricity / 4), 1)},
        {"label": "Diet", "impact": round(min(100.0, meat * 6.5), 1)},
        {"label": "Flights", "impact": round(min(100.0, flights * 10), 1)},
        {"label": "Recycling", "impact": round(min(100.0, recycling * 8), 1)},
    ]


def analyze_lifestyle(payload: Dict[str, float]) -> Dict[str, object]:
    daily_car = to_float(payload, "daily_car_km")
    daily_public = to_float(payload, "daily_public_transport_km")
    electricity = to_float(payload, "monthly_electricity_kwh")
    meat = to_float(payload, "meat_meals_per_week")
    flights = to_float(payload, "flights_per_year")
    recycling = to_float(payload, "recycling_frequency")

    emissions = calculate_emissions(daily_car, daily_public, electricity, meat, flights, recycling)
    monthly_co2 = max(
        0.0,
        round(
            emissions["transport_emissions"]
            + emissions["home_emissions"]
            + emissions["diet_emissions"]
            + emissions["travel_emissions"]
            - emissions["recycling_credit"],
            2,
        ),
    )

    source_scores = build_source_scores(daily_car, daily_public, electricity, meat, flights, recycling)
    score = calculate_score(daily_car, daily_public, electricity, meat, flights, recycling)
    category_breakdown = build_category_breakdown(emissions)

    positive_sources = {k: v for k, v in category_breakdown.items() if v > 0}
    top_emission_source = max(positive_sources, key=lambda source: positive_sources[source]) if positive_sources else "Balanced lifestyle"

    insights = []
    if daily_car > daily_public:
        insights.append("Private vehicle use is dominating your transport emissions.")
    if electricity > 300:
        insights.append("Your electricity use is above a low-impact monthly range.")
    if meat >= 7:
        insights.append("Frequent meat meals are materially increasing your footprint.")
    if flights > 0:
        insights.append("Flights create a sharp annual spike in your carbon footprint.")
    if recycling >= 3:
        insights.append("Your recycling habit is helping offset part of your footprint.")

    if not insights:
        insights.append("Your current lifestyle mix is relatively balanced across major emission sources.")

    recommendations = []
    if daily_car > 0:
        recommendations.append("Replace short car trips with walking, cycling, or carpooling at least 2 days per week.")
    if electricity > 0:
        recommendations.append("Reduce standby power, switch to LEDs, and set cooling/heating targets.")
    if meat > 0:
        recommendations.append("Swap 2-3 meat meals per week for plant-based alternatives.")
    if flights > 0:
        recommendations.append("Bundle travel and choose rail or virtual meetings when possible.")
    if recycling < 3:
        recommendations.append("Increase recycling consistency and separate waste streams at home.")

    if not recommendations:
        recommendations.append("Keep your routine steady and look for one small reduction target each week.")

    reduction_opportunities = build_reduction_opportunities(daily_car, electricity, meat, flights, recycling)

    return {
        "carbon_score": int(score),
        "monthly_co2": monthly_co2,
        "sustainability_rating": sustainability_rating(score),
        "top_emission_source": top_emission_source,
        "source_scores": source_scores,
        "category_breakdown": category_breakdown,
        "insights": insights,
        "recommendations": recommendations,
        "reduction_opportunities": reduction_opportunities,
    }
