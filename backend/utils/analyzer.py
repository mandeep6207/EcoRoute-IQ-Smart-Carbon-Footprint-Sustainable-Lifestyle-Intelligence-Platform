from __future__ import annotations

from typing import Dict


def clamp(value: float, minimum: float = 0, maximum: float = 100) -> float:
    return max(minimum, min(maximum, value))


def sustainability_rating(score: float) -> str:
    if score <= 30:
        return "Eco Friendly"
    if score <= 70:
        return "Moderate Impact"
    return "High Impact"


def analyze_lifestyle(payload: Dict[str, float]) -> Dict[str, object]:
    daily_car = float(payload.get("daily_car_km", 0) or 0)
    daily_public = float(payload.get("daily_public_transport_km", 0) or 0)
    electricity = float(payload.get("monthly_electricity_kwh", 0) or 0)
    meat = float(payload.get("meat_meals_per_week", 0) or 0)
    flights = float(payload.get("flights_per_year", 0) or 0)
    recycling = float(payload.get("recycling_frequency", 0) or 0)

    transport_emissions = (daily_car * 30 * 0.192) + (daily_public * 30 * 0.055)
    home_emissions = electricity * 0.42
    diet_emissions = meat * 4.33 * 2.3
    travel_emissions = flights * 230 / 12
    recycling_credit = recycling * 1.2

    monthly_co2 = max(0.0, round(transport_emissions + home_emissions + diet_emissions + travel_emissions - recycling_credit, 2))

    source_scores = {
        "Car travel": round(daily_car * 0.8, 2),
        "Public transport": round(daily_public * 0.25, 2),
        "Electricity": round(electricity * 0.08, 2),
        "Food habits": round(meat * 2.5, 2),
        "Flights": round(flights * 8.0, 2),
        "Recycling": round(max(0.0, 15.0 - recycling * 1.5), 2),
    }

    score = clamp(round(
        source_scores["Car travel"]
        + source_scores["Public transport"]
        + source_scores["Electricity"]
        + source_scores["Food habits"]
        + source_scores["Flights"]
        - (recycling * 1.5),
        0,
    ))

    category_breakdown = {
        "Transport": round(transport_emissions, 2),
        "Home energy": round(home_emissions, 2),
        "Diet": round(diet_emissions, 2),
        "Flights": round(travel_emissions, 2),
        "Recycling credit": round(-recycling_credit, 2),
    }

    positive_sources = {k: v for k, v in category_breakdown.items() if v > 0}
    top_emission_source = max(positive_sources, key=positive_sources.get) if positive_sources else "Balanced lifestyle"

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

    reduction_opportunities = [
        {"label": "Car travel", "impact": round(min(100.0, daily_car * 4.0), 1)},
        {"label": "Electricity", "impact": round(min(100.0, electricity / 4), 1)},
        {"label": "Diet", "impact": round(min(100.0, meat * 6.5), 1)},
        {"label": "Flights", "impact": round(min(100.0, flights * 10), 1)},
        {"label": "Recycling", "impact": round(min(100.0, recycling * 8), 1)},
    ]

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
