from enum import Enum
from typing import NamedTuple

class ResourceType(str, Enum):
    METAL = "metal"
    CRYSTAL = "crystal"
    DEUTERIUM = "deuterium"
    ENERGY = "energy"
    DARK_MATTER = "dark_matter"

class PlanetType(int, Enum):
    PLANET = 1
    DEBRIS = 2
    MOON = 3

class Coordinate(NamedTuple):
    galaxy: int
    system: int
    position: int
    planet_type: PlanetType = PlanetType.PLANET

    def as_string(self) -> str:
        return f"[{self.galaxy}:{self.system}:{self.position}]"

class GameObjectType(str, Enum):
    BUILDING = "building"
    FACILITY = "facility"
    RESEARCH = "research"
    SHIP = "ship"
    DEFENSE = "defense"
