from python.app.schemas.enums import Coordinate, PlanetType
from python.app.services.flight_calculator import FlightCalculator
from python.app.services.resource_calculator import ResourceCalculator
from python.app.game_objects.buildings import calculate_metal_production, calculate_crystal_production

def test_distance_calculation():
    origin = Coordinate(galaxy=1, system=100, position=5)
    target_same_sys = Coordinate(galaxy=1, system=100, position=8)
    target_diff_sys = Coordinate(galaxy=1, system=150, position=5)
    target_diff_gal = Coordinate(galaxy=2, system=100, position=5)

    # In same system: abs(pos1 - pos2) * 5 + 1000 = 3 * 5 + 1000 = 1015
    assert FlightCalculator.calculate_distance(origin, target_same_sys) == 1015
    # Different system: abs(sys1 - sys2) * 95 + 2700 = 50 * 95 + 2700 = 7450
    assert FlightCalculator.calculate_distance(origin, target_diff_sys) == 7450
    # Different galaxy: abs(gal1 - gal2) * 20000 = 20000
    assert FlightCalculator.calculate_distance(origin, target_diff_gal) == 20000

def test_resource_production_formulas():
    # Level 1 Metal Mine: 30 * 1 * (1.1 ** 1) = 33
    prod_lvl1 = calculate_metal_production(level=1, economy_speed=1.0)
    assert round(prod_lvl1, 1) == 33.0

    # Production with energy ratio
    hourly = ResourceCalculator.calculate_hourly_production(
        metal_mine_level=10,
        crystal_mine_level=8,
        deuterium_synth_level=5,
        solar_plant_level=12,
    )
    assert hourly["metal"] > 0
    assert hourly["crystal"] > 0
    assert hourly["deuterium"] > 0
    assert hourly["energy_ratio"] == 1.0
