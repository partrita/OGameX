import math
from typing import Dict, Tuple
from python.app.schemas.enums import Coordinate

class FlightCalculator:
    """Calculates fleet distance, flight time, and fuel consumption based on OGame mechanics."""

    @staticmethod
    def calculate_distance(origin: Coordinate, target: Coordinate) -> int:
        """Calculates exact universe distance between coordinates."""
        if origin.galaxy != target.galaxy:
            return abs(origin.galaxy - target.galaxy) * 20000
        elif origin.system != target.system:
            return abs(origin.system - target.system) * 95 + 2700
        elif origin.position != target.position:
            return abs(origin.position - target.position) * 5 + 1000
        else:
            # Same position (e.g. planet to moon)
            return 5

    @staticmethod
    def calculate_flight_time_seconds(distance: int, max_fleet_speed: int, speed_percent: float = 1.0, universe_speed_fleet: float = 1.0) -> int:
        """
        Flight time formula:
        seconds = ((35000 / (speed_percent * 10)) * sqrt(distance * 10 / max_speed) + 10) / universe_speed_fleet
        """
        if max_fleet_speed <= 0 or speed_percent <= 0:
            return 0
        
        speed_factor = speed_percent * 10
        base_time = (35000.0 / speed_factor) * math.sqrt((distance * 10.0) / max_fleet_speed) + 10.0
        return max(5, int(math.ceil(base_time / universe_speed_fleet)))

    @staticmethod
    def calculate_fuel_consumption(distance: int, flight_time_seconds: int, ship_fuel_usage: int, ship_speed: int, speed_percent: float = 1.0) -> int:
        """
        Fuel consumption per ship:
        1 + round((ship_fuel_usage * distance / 35000) * ((speed_percent / 10 + 1) ** 2))
        """
        factor = ((speed_percent * 10) / 10.0 + 1.0) ** 2
        consumption = 1 + round((ship_fuel_usage * distance / 35000.0) * factor)
        return int(consumption)
