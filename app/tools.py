
ROOF_COEFFICIENTS = {
    "gi sheet": 0.90,
    "asbestos": 0.80,
    "tiled roof": 0.75,
    "concrete roof": 0.70,
}


def rooftop_rainwater_calculator(
    rainfall_mm: float,
    roof_area_sqm: float,
    roof_type: str,
    persons: int,
    litres_per_person_per_day: float,
    dry_days: int
) -> dict:
    """
    Calculate annual rooftop rainwater collection
    and compare it with household water demand.
    """

    # Validate inputs
    if rainfall_mm <= 0:
        raise ValueError("Rainfall must be greater than zero.")

    if roof_area_sqm <= 0:
        raise ValueError("Roof area must be greater than zero.")

    if persons <= 0 or dry_days <= 0:
        raise ValueError("Persons and dry days must be greater than zero.")

    if litres_per_person_per_day <= 0:
        raise ValueError("Daily water requirement must be greater than zero.")

    roof_type = roof_type.strip().lower()

    if roof_type not in ROOF_COEFFICIENTS:
        raise ValueError(
            f"Unsupported roof type. Choose from: "
            f"{', '.join(ROOF_COEFFICIENTS.keys())}"
        )

    # Get runoff coefficient
    coefficient = ROOF_COEFFICIENTS[roof_type]

    # Calculate annual rainwater collection
    annual_collection = (
        rainfall_mm * roof_area_sqm * coefficient
    )

    # Calculate household demand during dry days
    household_demand = (
        persons * litres_per_person_per_day * dry_days
    )

    # Compare collection with demand
    difference = annual_collection - household_demand

    coverage = (
        annual_collection / household_demand
    ) * 100

    return {
        "roof_type": roof_type,
        "runoff_coefficient": coefficient,
        "annual_rainwater_collection_litres": round(
            annual_collection, 2
        ),
        "household_demand_litres": round(
            household_demand, 2
        ),
        "surplus_or_deficit_litres": round(
            difference, 2
        ),
        "demand_covered": annual_collection >= household_demand,
        "demand_coverage_percentage": round(coverage, 2)
    }
