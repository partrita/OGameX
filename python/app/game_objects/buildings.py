import math
from typing import Dict
from python.app.game_objects.models import BuildingObject, GameObjectPrice

BUILDINGS: Dict[int, BuildingObject] = {}

# Metal Mine (ID 1)
BUILDINGS[1] = BuildingObject(
    id=1,
    machine_name="metal_mine",
    title="Metal Mine",
    class_name="metalMine",
    description="Used in the extraction of metal ore.",
    price=GameObjectPrice(metal=60, crystal=15, deuterium=0, energy=0, factor=1.5),
)

# Crystal Mine (ID 2)
BUILDINGS[2] = BuildingObject(
    id=2,
    machine_name="crystal_mine",
    title="Crystal Mine",
    class_name="crystalMine",
    description="Crystals are the main resource used to build electronic circuits and form certain alloy compounds.",
    price=GameObjectPrice(metal=48, crystal=24, deuterium=0, energy=0, factor=1.6),
)

# Deuterium Synthesizer (ID 3)
BUILDINGS[3] = BuildingObject(
    id=3,
    machine_name="deuterium_synthesizer",
    title="Deuterium Synthesizer",
    class_name="deuteriumSynthesizer",
    description="Deuterium is used as fuel for spaceships and in research.",
    price=GameObjectPrice(metal=225, crystal=75, deuterium=0, energy=0, factor=1.5),
)

# Solar Plant (ID 4)
BUILDINGS[4] = BuildingObject(
    id=4,
    machine_name="solar_plant",
    title="Solar Plant",
    class_name="solarPlant",
    description="Solar power plants absorb energy from solar radiation.",
    price=GameObjectPrice(metal=75, crystal=30, deuterium=0, energy=0, factor=1.5),
)

# Robotic Factory (ID 14)
BUILDINGS[14] = BuildingObject(
    id=14,
    machine_name="robot_factory",
    title="Robotics Factory",
    class_name="robotFactory",
    description="Robotics factories provide simple construction robots to aid in the construction of buildings.",
    price=GameObjectPrice(metal=400, crystal=120, deuterium=200, energy=0, factor=2.0),
)

# Shipyard (ID 21)
BUILDINGS[21] = BuildingObject(
    id=21,
    machine_name="shipyard",
    title="Shipyard",
    class_name="shipyard",
    description="Planetary and lunar shipyards allow the construction of all types of ships and defensive facilities.",
    price=GameObjectPrice(metal=400, crystal=200, deuterium=100, energy=0, factor=2.0),
)

# Research Lab (ID 31)
BUILDINGS[31] = BuildingObject(
    id=31,
    machine_name="research_lab",
    title="Research Lab",
    class_name="researchLab",
    description="A research lab is required to conduct research into new technologies.",
    price=GameObjectPrice(metal=200, crystal=400, deuterium=200, energy=0, factor=2.0),
)

# Production Formulas
def calculate_metal_production(level: int, economy_speed: float = 1.0) -> float:
    if level == 0:
        return 0.0
    return 30 * level * (1.1 ** level) * economy_speed

def calculate_metal_energy_consumption(level: int) -> float:
    if level == 0:
        return 0.0
    return 10 * level * (1.1 ** level)

def calculate_crystal_production(level: int, economy_speed: float = 1.0) -> float:
    if level == 0:
        return 0.0
    return 20 * level * (1.1 ** level) * economy_speed

def calculate_crystal_energy_consumption(level: int) -> float:
    if level == 0:
        return 0.0
    return 10 * level * (1.1 ** level)

def calculate_deuterium_production(level: int, max_temp: int, economy_speed: float = 1.0) -> float:
    if level == 0:
        return 0.0
    temp_factor = 1.05 + (-0.005 * max_temp)
    return 10 * level * (1.1 ** level) * temp_factor * economy_speed

def calculate_deuterium_energy_consumption(level: int) -> float:
    if level == 0:
        return 0.0
    return 20 * level * (1.1 ** level)

def calculate_solar_plant_production(level: int) -> float:
    if level == 0:
        return 0.0
    return 20 * level * (1.1 ** level)

def calculate_building_storage(level: int) -> int:
    """Storage capacity formula: 5000 * floor(2.5 * e^(20 * level / 33))"""
    if level == 0:
        return 10000
    return int(5000 * math.floor(2.5 * math.exp(20 * level / 33)))
