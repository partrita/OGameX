from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class CoordinateSchema(BaseModel):
    galaxy: int = Field(..., ge=1, le=9)
    system: int = Field(..., ge=1, le=499)
    position: int = Field(..., ge=1, le=16)
    planet_type: int = 1

class ResourceSummary(BaseModel):
    metal: float
    crystal: float
    deuterium: float
    energy: float
    max_metal_storage: int
    max_crystal_storage: int
    max_deuterium_storage: int
    metal_production_hourly: float = 0.0
    crystal_production_hourly: float = 0.0
    deuterium_production_hourly: float = 0.0

class ActiveFleetMission(BaseModel):
    id: int
    mission_type: str
    target_galaxy: int
    target_system: int
    target_position: int
    ships_count: int
    arrival_time_remaining: int # seconds left
    status: str # "flying", "returning"
    fuel_used: int

class PlanetOverview(BaseModel):
    id: int
    name: str
    coordinates: CoordinateSchema
    diameter: int
    fields_used: int
    max_fields: int
    temp_min: int
    temp_max: int
    resources: ResourceSummary
    active_missions: List[ActiveFleetMission] = []


class BuildingItem(BaseModel):
    id: int
    machine_name: str
    title: str
    description: str
    level: int
    cost_metal: int
    cost_crystal: int
    cost_deuterium: int
    cost_energy: int
    production_hourly: Optional[float] = 0.0
    energy_diff: Optional[float] = 0.0
    can_build: bool = True

class BuildingsResponse(BaseModel):
    planet_id: int
    buildings: List[BuildingItem]

class UpgradeBuildingRequest(BaseModel):
    building_id: int

class ShipItem(BaseModel):
    id: int
    machine_name: str
    title: str
    description: str
    count: int
    cost_metal: int
    cost_crystal: int
    cost_deuterium: int
    structural_integrity: int
    shield_power: int
    weapon_power: int
    cargo_capacity: int
    base_speed: int
    fuel_consumption: int
    can_build: bool = True

class ShipyardResponse(BaseModel):
    planet_id: int
    ships: List[ShipItem]

class BuildShipRequest(BaseModel):
    ship_id: int
    amount: int = Field(..., ge=1)

class GalaxySlot(BaseModel):
    position: int
    planet_name: Optional[str] = None
    player_name: Optional[str] = None
    alliance_tag: Optional[str] = None
    is_player: bool = False
    status: Optional[str] = None
    debris_metal: int = 0
    debris_crystal: int = 0

class GalaxyResponse(BaseModel):
    galaxy: int
    system: int
    slots: List[GalaxySlot]

class FleetDispatchCheckRequest(BaseModel):
    origin_planet_id: int
    target: CoordinateSchema
    ships: Dict[int, int] # unit_id -> count
    speed_percent: float = 1.0 # 0.1 to 1.0

class FleetDispatchCheckResponse(BaseModel):
    valid: bool
    distance: int
    flight_time_seconds: int
    fuel_consumption: int
    cargo_capacity: int
    max_fleet_speed: int
    message: Optional[str] = None

class FleetSendRequest(BaseModel):
    origin_planet_id: int
    target: CoordinateSchema
    mission_type: str = "transport" # transport, deploy, attack, harvest
    ships: Dict[int, int]
    resources: Dict[str, float] = {"metal": 0, "crystal": 0, "deuterium": 0}
    speed_percent: float = 1.0

class FleetSendResponse(BaseModel):
    success: bool
    message: str
    flight_time_seconds: int
    fuel_consumed: int

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=30)
    password: str = Field(..., min_length=4)
    planet_name: Optional[str] = "Homeworld"

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    planet_id: int
    token: str
    message: str

