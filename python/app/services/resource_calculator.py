import math
import time
from typing import Dict, Tuple
from python.app.game_objects.buildings import (
    calculate_metal_production,
    calculate_metal_energy_consumption,
    calculate_crystal_production,
    calculate_crystal_energy_consumption,
    calculate_deuterium_production,
    calculate_deuterium_energy_consumption,
    calculate_solar_plant_production,
    calculate_building_storage,
)

class ResourceCalculator:
    """Computes planet resource production, storage limits, and energy balance in real-time."""

    @staticmethod
    def calculate_energy_balance(
        solar_plant_level: int,
        metal_mine_level: int,
        crystal_mine_level: int,
        deuterium_synth_level: int,
    ) -> Tuple[float, float, float]:
        """Returns (energy_produced, energy_consumed, production_ratio [0.0 - 1.0])"""
        energy_produced = calculate_solar_plant_production(solar_plant_level)
        
        energy_consumed = (
            calculate_metal_energy_consumption(metal_mine_level)
            + calculate_crystal_energy_consumption(crystal_mine_level)
            + calculate_deuterium_energy_consumption(deuterium_synth_level)
        )
        
        if energy_consumed == 0:
            ratio = 1.0
        elif energy_produced >= energy_consumed:
            ratio = 1.0
        else:
            ratio = max(0.0, energy_produced / energy_consumed)
            
        return energy_produced, energy_consumed, ratio

    @staticmethod
    def calculate_hourly_production(
        metal_mine_level: int,
        crystal_mine_level: int,
        deuterium_synth_level: int,
        solar_plant_level: int,
        max_temp: int = 40,
        economy_speed: float = 1.0,
    ) -> Dict[str, float]:
        """Calculates effective resource production per hour with energy ratio factored in."""
        _, _, ratio = ResourceCalculator.calculate_energy_balance(
            solar_plant_level, metal_mine_level, crystal_mine_level, deuterium_synth_level
        )
        
        # Base planetary production (30 metal, 15 crystal)
        base_metal = 30.0 * economy_speed
        base_crystal = 15.0 * economy_speed
        
        metal_prod = base_metal + calculate_metal_production(metal_mine_level, economy_speed) * ratio
        crystal_prod = base_crystal + calculate_crystal_production(crystal_mine_level, economy_speed) * ratio
        deut_prod = calculate_deuterium_production(deuterium_synth_level, max_temp, economy_speed) * ratio
        
        return {
            "metal": metal_prod,
            "crystal": crystal_prod,
            "deuterium": deut_prod,
            "energy_ratio": ratio,
        }

    @staticmethod
    def update_resources_for_elapsed_time(
        current_resources: Dict[str, float],
        hourly_production: Dict[str, float],
        elapsed_seconds: float,
        storages: Dict[str, int],
    ) -> Dict[str, float]:
        """Accrues resources according to elapsed time and caps at maximum storage capacity."""
        updated = {}
        for res in ["metal", "crystal", "deuterium"]:
            gain = (hourly_production[res] / 3600.0) * elapsed_seconds
            current = current_resources.get(res, 0.0)
            storage = storages.get(res, 10000)
            
            # If already above storage, do not cap down, but do not produce more
            if current >= storage:
                updated[res] = current
            else:
                updated[res] = min(float(storage), current + gain)
                
        return updated
