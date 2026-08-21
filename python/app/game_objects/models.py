import math
from typing import Callable, Optional, Dict, List
from pydantic import BaseModel, Field

class GameObjectPrice(BaseModel):
    metal: int = 0
    crystal: int = 0
    deuterium: int = 0
    energy: int = 0
    factor: float = 1.0

    def calculate_price_for_level(self, level: int) -> "GameObjectPrice":
        """Calculates upgrade cost for a specific building/research level."""
        if level <= 1:
            return self
        multiplier = self.factor ** (level - 1)
        return GameObjectPrice(
            metal=math.floor(self.metal * multiplier),
            crystal=math.floor(self.crystal * multiplier),
            deuterium=math.floor(self.deuterium * multiplier),
            energy=math.floor(self.energy * multiplier),
            factor=self.factor
        )

class GameObject(BaseModel):
    id: int
    machine_name: str
    title: str
    class_name: str
    description: str
    price: GameObjectPrice
    type: str

class BuildingObject(GameObject):
    type: str = "building"
    metal_production: Optional[Callable[[int, float], float]] = None
    crystal_production: Optional[Callable[[int, float], float]] = None
    deuterium_production: Optional[Callable[[int, float, float], float]] = None
    energy_production: Optional[Callable[[int, float], float]] = None
    energy_consumption: Optional[Callable[[int, float], float]] = None
    storage_capacity: Optional[Callable[[int], int]] = None

class ShipObject(GameObject):
    type: str = "ship"
    structural_integrity: int
    shield_power: int
    weapon_power: int
    cargo_capacity: int
    base_speed: int
    fuel_consumption: int
    rapidfire: Dict[int, int] = Field(default_factory=dict)
