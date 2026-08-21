import random
import time
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from python.app.schemas.planet import (
    PlanetOverview,
    CoordinateSchema,
    ResourceSummary,
    ActiveFleetMission,
    BuildingItem,
    BuildingsResponse,
    UpgradeBuildingRequest,
    ShipItem,
    ShipyardResponse,
    BuildShipRequest,
    GalaxySlot,
    GalaxyResponse,
    FleetDispatchCheckRequest,
    FleetDispatchCheckResponse,
    FleetSendRequest,
    FleetSendResponse,
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
)
from python.app.schemas.enums import Coordinate, PlanetType
from python.app.game_objects.ships import SHIPS
from python.app.game_objects.buildings import (
    BUILDINGS,
    calculate_building_storage,
    calculate_metal_production,
    calculate_crystal_production,
    calculate_deuterium_production,
    calculate_solar_plant_production,
    calculate_metal_energy_consumption,
    calculate_crystal_energy_consumption,
    calculate_deuterium_energy_consumption,
)
from python.app.services.flight_calculator import FlightCalculator
from python.app.services.resource_calculator import ResourceCalculator

router = APIRouter()

# Multi-user dynamic in-memory database
USERS_DB: Dict[str, Dict[str, Any]] = {
    "admin": {
        "id": 1,
        "username": "admin",
        "password": "password",
        "planet_id": 1
    }
}

# In-memory fleet missions queue
# mission_id -> {id, planet_id, mission_type, target, ships, start_time, duration, status, fuel}
FLEET_MISSIONS: List[Dict[str, Any]] = []
NEXT_MISSION_ID = 1

PLANETS_DB: Dict[int, Dict[str, Any]] = {
    1: {
        "id": 1,
        "user_id": 1,
        "username": "admin",
        "name": "Homeworld",
        "coordinates": {"galaxy": 1, "system": 100, "position": 5, "planet_type": 1},
        "diameter": 12800,
        "fields_used": 51,
        "max_fields": 163,
        "temp_min": -10,
        "temp_max": 30,
        "last_updated": time.time(),
        "resources": {
            "metal": 25400.0,
            "crystal": 14200.0,
            "deuterium": 8300.0,
        },
        "buildings": {
            1: 15, # Metal Mine
            2: 12, # Crystal Mine
            3: 8,  # Deuterium Synth
            4: 12, # Solar Plant
            14: 4, # Robotics Factory
            21: 5, # Shipyard
            31: 3, # Research Lab
        },
        "ships": {
            202: 10, # Small Cargo
            203: 2,  # Large Cargo
            204: 15, # Light Fighter
            206: 4,  # Cruiser
            207: 1,  # Battleship
            214: 0,  # Deathstar
        }
    }
}

NEXT_USER_ID = 2
NEXT_PLANET_ID = 2

def update_planet_resources(state: Dict[str, Any]):
    """Calculates and accumulates mined resources based on elapsed seconds since last update."""
    now = time.time()
    last_time = state.get("last_updated", now)
    elapsed_seconds = max(0.0, now - last_time)
    state["last_updated"] = now

    b = state["buildings"]
    solar_plant_lvl = b.get(4, 0)
    metal_mine_lvl = b.get(1, 0)
    crystal_mine_lvl = b.get(2, 0)
    deut_synth_lvl = b.get(3, 0)

    # Hourly rates
    metal_hourly = calculate_metal_production(metal_mine_lvl)
    crystal_hourly = calculate_crystal_production(crystal_mine_lvl)
    deut_hourly = calculate_deuterium_production(deut_synth_lvl, state["temp_max"])

    # Energy ratio check
    energy_prod, energy_cons, energy_ratio = ResourceCalculator.calculate_energy_balance(
        solar_plant_lvl, metal_mine_lvl, crystal_mine_lvl, deut_synth_lvl
    )

    metal_gain = (metal_hourly / 3600.0) * elapsed_seconds * energy_ratio
    crystal_gain = (crystal_hourly / 3600.0) * elapsed_seconds * energy_ratio
    deut_gain = (deut_hourly / 3600.0) * elapsed_seconds * energy_ratio

    metal_storage = calculate_building_storage(level=4)
    crystal_storage = calculate_building_storage(level=3)
    deut_storage = calculate_building_storage(level=2)

    state["resources"]["metal"] = min(float(metal_storage), state["resources"]["metal"] + metal_gain)
    state["resources"]["crystal"] = min(float(crystal_storage), state["resources"]["crystal"] + crystal_gain)
    state["resources"]["deuterium"] = min(float(deut_storage), state["resources"]["deuterium"] + deut_gain)

    return {
        "metal_hourly": metal_hourly * energy_ratio,
        "crystal_hourly": crystal_hourly * energy_ratio,
        "deut_hourly": deut_hourly * energy_ratio,
        "energy_prod": energy_prod,
        "energy_cons": energy_cons,
        "metal_storage": metal_storage,
        "crystal_storage": crystal_storage,
        "deut_storage": deut_storage,
    }

@router.post("/auth/register", response_model=UserResponse)
async def register(req: UserRegisterRequest):
    global NEXT_USER_ID, NEXT_PLANET_ID
    username_lower = req.username.strip().lower()
    if username_lower in USERS_DB:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자 이름입니다.")

    user_id = NEXT_USER_ID
    NEXT_USER_ID += 1

    planet_id = NEXT_PLANET_ID
    NEXT_PLANET_ID += 1

    occupied_coords = {(p["coordinates"]["galaxy"], p["coordinates"]["system"], p["coordinates"]["position"]) for p in PLANETS_DB.values()}
    assigned_pos = None
    for attempt in range(100):
        g = random.randint(1, 2)
        s = random.randint(100, 105)
        p = random.randint(4, 12)
        if (g, s, p) not in occupied_coords:
            assigned_pos = (g, s, p)
            break
    if not assigned_pos:
        assigned_pos = (1, 100, (planet_id % 15) + 1)

    USERS_DB[username_lower] = {
        "id": user_id,
        "username": req.username,
        "password": req.password,
        "planet_id": planet_id
    }

    PLANETS_DB[planet_id] = {
        "id": planet_id,
        "user_id": user_id,
        "username": req.username,
        "name": req.planet_name or f"{req.username}의 행성",
        "coordinates": {"galaxy": assigned_pos[0], "system": assigned_pos[1], "position": assigned_pos[2], "planet_type": 1},
        "diameter": 12800 + random.randint(-500, 500),
        "fields_used": 15,
        "max_fields": 163,
        "temp_min": -15,
        "temp_max": 35,
        "last_updated": time.time(),
        "resources": {
            "metal": 10000.0,
            "crystal": 5000.0,
            "deuterium": 2000.0,
        },
        "buildings": {
            1: 4,  # Metal Mine
            2: 3,  # Crystal Mine
            3: 1,  # Deuterium Synth
            4: 4,  # Solar Plant
            14: 1, # Robotics Factory
            21: 1, # Shipyard
            31: 0, # Research Lab
        },
        "ships": {
            202: 2,  # Small Cargo
            203: 0,
            204: 3,  # Light Fighter
            206: 0,
            207: 0,
            214: 0,
        }
    }

    return UserResponse(
        id=user_id,
        username=req.username,
        planet_id=planet_id,
        token=f"user_token_{user_id}",
        message="회원가입이 완료되었습니다!"
    )

@router.post("/auth/login", response_model=UserResponse)
async def login(req: UserLoginRequest):
    username_lower = req.username.strip().lower()
    user = USERS_DB.get(username_lower)
    if not user or user["password"] != req.password:
        raise HTTPException(status_code=400, detail="사용자 이름 또는 비밀번호가 올바르지 않습니다.")

    return UserResponse(
        id=user["id"],
        username=user["username"],
        planet_id=user["planet_id"],
        token=f"user_token_{user['id']}",
        message="로그인 성공!"
    )

@router.get("/planet/{planet_id}/overview", response_model=PlanetOverview)
async def get_planet_overview(planet_id: int):
    """Calculates real-time planet status, accumulated production, and active missions."""
    state = PLANETS_DB.get(planet_id, PLANETS_DB.get(1))
    if not state:
        raise HTTPException(status_code=404, detail="Planet not found")

    stats = update_planet_resources(state)
    b = state["buildings"]

    # Active missions check
    now = time.time()
    active_missions_list = []
    for m in FLEET_MISSIONS:
        if m["origin_planet_id"] == planet_id:
            elapsed = now - m["start_time"]
            total_duration = m["duration"]
            remaining = int(max(0, total_duration - elapsed))
            if remaining > 0:
                active_missions_list.append(
                    ActiveFleetMission(
                        id=m["id"],
                        mission_type=m["mission_type"],
                        target_galaxy=m["target"]["galaxy"],
                        target_system=m["target"]["system"],
                        target_position=m["target"]["position"],
                        ships_count=sum(m["ships"].values()),
                        arrival_time_remaining=remaining,
                        status="flying",
                        fuel_used=m["fuel_consumed"]
                    )
                )

    return PlanetOverview(
        id=planet_id,
        name=state["name"],
        coordinates=CoordinateSchema(**state["coordinates"]),
        diameter=state["diameter"],
        fields_used=sum(b.values()),
        max_fields=state["max_fields"],
        temp_min=state["temp_min"],
        temp_max=state["temp_max"],
        resources=ResourceSummary(
            metal=state["resources"]["metal"],
            crystal=state["resources"]["crystal"],
            deuterium=state["resources"]["deuterium"],
            energy=stats["energy_prod"] - stats["energy_cons"],
            max_metal_storage=stats["metal_storage"],
            max_crystal_storage=stats["crystal_storage"],
            max_deuterium_storage=stats["deut_storage"],
            metal_production_hourly=stats["metal_hourly"],
            crystal_production_hourly=stats["crystal_hourly"],
            deuterium_production_hourly=stats["deut_hourly"],
        ),
        active_missions=active_missions_list
    )


@router.get("/planet/{planet_id}/resources", response_model=BuildingsResponse)
async def get_planet_resources(planet_id: int):
    """Returns resource-producing buildings with upgrade cost and production stats."""
    state = PLANETS_DB.get(planet_id, PLANETS_DB.get(1))
    if not state:
        raise HTTPException(status_code=404, detail="Planet not found")
    resource_building_ids = [1, 2, 3, 4]
    items = []

    for bid in resource_building_ids:
        b_obj = BUILDINGS[bid]
        lvl = state["buildings"].get(bid, 0)
        cost_m = int(b_obj.price.metal * (b_obj.price.factor ** lvl))
        cost_c = int(b_obj.price.crystal * (b_obj.price.factor ** lvl))
        cost_d = int(b_obj.price.deuterium * (b_obj.price.factor ** lvl))
        cost_e = int(b_obj.price.energy * (b_obj.price.factor ** lvl))

        prod = 0.0
        if bid == 1:
            prod = calculate_metal_production(lvl)
        elif bid == 2:
            prod = calculate_crystal_production(lvl)
        elif bid == 3:
            prod = calculate_deuterium_production(lvl, state["temp_max"])
        elif bid == 4:
            prod = calculate_solar_plant_production(lvl)

        can_afford = (
            state["resources"]["metal"] >= cost_m and
            state["resources"]["crystal"] >= cost_c and
            state["resources"]["deuterium"] >= cost_d
        )

        items.append(
            BuildingItem(
                id=bid,
                machine_name=b_obj.machine_name,
                title=b_obj.title,
                description=b_obj.description,
                level=lvl,
                cost_metal=cost_m,
                cost_crystal=cost_c,
                cost_deuterium=cost_d,
                cost_energy=cost_e,
                production_hourly=prod,
                can_build=can_afford
            )
        )
    return BuildingsResponse(planet_id=planet_id, buildings=items)

@router.get("/planet/{planet_id}/facilities", response_model=BuildingsResponse)
async def get_planet_facilities(planet_id: int):
    """Returns facility buildings (Robotics, Shipyard, Lab) stats and levels."""
    state = PLANETS_DB.get(planet_id, PLANETS_DB.get(1))
    if not state:
        raise HTTPException(status_code=404, detail="Planet not found")
    facility_building_ids = [14, 21, 31]
    items = []

    for bid in facility_building_ids:
        b_obj = BUILDINGS[bid]
        lvl = state["buildings"].get(bid, 0)
        cost_m = int(b_obj.price.metal * (b_obj.price.factor ** lvl))
        cost_c = int(b_obj.price.crystal * (b_obj.price.factor ** lvl))
        cost_d = int(b_obj.price.deuterium * (b_obj.price.factor ** lvl))
        cost_e = int(b_obj.price.energy * (b_obj.price.factor ** lvl))

        can_afford = (
            state["resources"]["metal"] >= cost_m and
            state["resources"]["crystal"] >= cost_c and
            state["resources"]["deuterium"] >= cost_d
        )

        items.append(
            BuildingItem(
                id=bid,
                machine_name=b_obj.machine_name,
                title=b_obj.title,
                description=b_obj.description,
                level=lvl,
                cost_metal=cost_m,
                cost_crystal=cost_c,
                cost_deuterium=cost_d,
                cost_energy=cost_e,
                production_hourly=0.0,
                can_build=can_afford
            )
        )
    return BuildingsResponse(planet_id=planet_id, buildings=items)

@router.post("/planet/{planet_id}/buildings/upgrade")
async def upgrade_building(planet_id: int, req: UpgradeBuildingRequest):
    """Upgrades a building and deducts resources."""
    state = PLANETS_DB.get(planet_id)
    if not state:
        raise HTTPException(status_code=404, detail="Planet not found")

    bid = req.building_id
    if bid not in BUILDINGS:
        raise HTTPException(status_code=400, detail="Invalid building ID")

    b_obj = BUILDINGS[bid]
    lvl = state["buildings"].get(bid, 0)
    cost_m = int(b_obj.price.metal * (b_obj.price.factor ** lvl))
    cost_c = int(b_obj.price.crystal * (b_obj.price.factor ** lvl))
    cost_d = int(b_obj.price.deuterium * (b_obj.price.factor ** lvl))

    if (
        state["resources"]["metal"] < cost_m or
        state["resources"]["crystal"] < cost_c or
        state["resources"]["deuterium"] < cost_d
    ):
        raise HTTPException(status_code=400, detail="Not enough resources")

    state["resources"]["metal"] -= cost_m
    state["resources"]["crystal"] -= cost_c
    state["resources"]["deuterium"] -= cost_d
    state["buildings"][bid] = lvl + 1

    return {"success": True, "new_level": lvl + 1, "remaining_resources": state["resources"]}

@router.get("/planet/{planet_id}/shipyard", response_model=ShipyardResponse)
async def get_shipyard(planet_id: int):
    """Returns all buildable ships and current hangar counts."""
    state = PLANETS_DB.get(planet_id, PLANETS_DB.get(1))
    if not state:
        raise HTTPException(status_code=404, detail="Planet not found")
    ship_items = []

    for sid, s_obj in SHIPS.items():
        count = state["ships"].get(sid, 0)
        can_afford = (
            state["resources"]["metal"] >= s_obj.price.metal and
            state["resources"]["crystal"] >= s_obj.price.crystal and
            state["resources"]["deuterium"] >= s_obj.price.deuterium
        )
        ship_items.append(
            ShipItem(
                id=sid,
                machine_name=s_obj.machine_name,
                title=s_obj.title,
                description=s_obj.description,
                count=count,
                cost_metal=s_obj.price.metal,
                cost_crystal=s_obj.price.crystal,
                cost_deuterium=s_obj.price.deuterium,
                structural_integrity=s_obj.structural_integrity,
                shield_power=s_obj.shield_power,
                weapon_power=s_obj.weapon_power,
                cargo_capacity=s_obj.cargo_capacity,
                base_speed=s_obj.base_speed,
                fuel_consumption=s_obj.fuel_consumption,
                can_build=can_afford
            )
        )
    return ShipyardResponse(planet_id=planet_id, ships=ship_items)

@router.post("/planet/{planet_id}/shipyard/build")
async def build_ship(planet_id: int, req: BuildShipRequest):
    """Builds ships and immediately adds them to planet hangar."""
    state = PLANETS_DB.get(planet_id)
    if not state:
        raise HTTPException(status_code=404, detail="Planet not found")

    sid = req.ship_id
    if sid not in SHIPS:
        raise HTTPException(status_code=400, detail="Invalid ship ID")

    ship = SHIPS[sid]
    total_m = ship.price.metal * req.amount
    total_c = ship.price.crystal * req.amount
    total_d = ship.price.deuterium * req.amount

    if (
        state["resources"]["metal"] < total_m or
        state["resources"]["crystal"] < total_c or
        state["resources"]["deuterium"] < total_d
    ):
        raise HTTPException(status_code=400, detail="Not enough resources")

    state["resources"]["metal"] -= total_m
    state["resources"]["crystal"] -= total_c
    state["resources"]["deuterium"] -= total_d
    state["ships"][sid] = state["ships"].get(sid, 0) + req.amount

    return {
        "success": True,
        "built": req.amount,
        "total_count": state["ships"][sid],
        "remaining_resources": state["resources"]
    }

@router.get("/galaxy/{galaxy}/{system}", response_model=GalaxyResponse)
async def get_galaxy_system(galaxy: int, system: int):
    """Returns 1~16 planetary slots in the specified solar system dynamically."""
    system_planets = {
        p["coordinates"]["position"]: p
        for p in PLANETS_DB.values()
        if p["coordinates"]["galaxy"] == galaxy and p["coordinates"]["system"] == system
    }

    slots = []
    for pos in range(1, 17):
        if pos in system_planets:
            p = system_planets[pos]
            slots.append(
                GalaxySlot(
                    position=pos,
                    planet_name=p["name"],
                    player_name=p["username"],
                    alliance_tag="OGX" if p["user_id"] == 1 else "NOVA",
                    is_player=True,
                    status="online",
                    debris_metal=random.randint(500, 3000),
                    debris_crystal=random.randint(200, 1500)
                )
            )
        elif pos == 16:
            slots.append(
                GalaxySlot(
                    position=pos,
                    planet_name="Deep Space (Expedition)",
                    player_name=None,
                    alliance_tag=None,
                    is_player=False,
                    status=None
                )
            )
        else:
            slots.append(
                GalaxySlot(
                    position=pos,
                    planet_name=None,
                    player_name=None,
                    alliance_tag=None,
                    is_player=False,
                    status=None
                )
            )

    return GalaxyResponse(galaxy=galaxy, system=system, slots=slots)

@router.post("/fleet/dispatch/check", response_model=FleetDispatchCheckResponse)
async def check_fleet_dispatch(req: FleetDispatchCheckRequest):
    """Calculates exact flight time, distance, cargo capacity, and fuel usage."""
    if not req.ships:
        raise HTTPException(status_code=400, detail="No ships selected for fleet dispatch.")

    origin_planet = PLANETS_DB.get(req.origin_planet_id, PLANETS_DB.get(1))
    origin_coord = Coordinate(
        galaxy=origin_planet["coordinates"]["galaxy"],
        system=origin_planet["coordinates"]["system"],
        position=origin_planet["coordinates"]["position"]
    )
    target_coord = Coordinate(
        galaxy=req.target.galaxy,
        system=req.target.system,
        position=req.target.position,
        planet_type=PlanetType(req.target.planet_type),
    )

    distance = FlightCalculator.calculate_distance(origin_coord, target_coord)

    min_speed = 999999
    total_cargo = 0
    total_fuel_consumption = 0

    for ship_id, count in req.ships.items():
        if ship_id not in SHIPS or count <= 0:
            continue
        ship = SHIPS[ship_id]
        if ship.base_speed < min_speed:
            min_speed = ship.base_speed
        total_cargo += ship.cargo_capacity * count

    if min_speed == 999999:
        min_speed = 5000

    flight_time = FlightCalculator.calculate_flight_time_seconds(
        distance=distance,
        max_fleet_speed=min_speed,
        speed_percent=req.speed_percent,
        universe_speed_fleet=1.0,
    )

    for ship_id, count in req.ships.items():
        if ship_id not in SHIPS or count <= 0:
            continue
        ship = SHIPS[ship_id]
        fuel_per_ship = FlightCalculator.calculate_fuel_consumption(
            distance=distance,
            flight_time_seconds=flight_time,
            ship_fuel_usage=ship.fuel_consumption,
            ship_speed=ship.base_speed,
            speed_percent=req.speed_percent,
        )
        total_fuel_consumption += fuel_per_ship * count

    return FleetDispatchCheckResponse(
        valid=True,
        distance=distance,
        flight_time_seconds=flight_time,
        fuel_consumption=total_fuel_consumption,
        cargo_capacity=total_cargo,
        max_fleet_speed=min_speed,
        message="Fleet calculation successful.",
    )

@router.post("/fleet/dispatch/send", response_model=FleetSendResponse)
async def send_fleet(req: FleetSendRequest):
    """Dispatches fleet to target destination and deducts ships/fuel."""
    state = PLANETS_DB.get(req.origin_planet_id, PLANETS_DB.get(1))
    if not state:
        raise HTTPException(status_code=404, detail="Origin planet not found")

    # Check ship availability
    for sid, count in req.ships.items():
        if state["ships"].get(sid, 0) < count:
            raise HTTPException(status_code=400, detail=f"Not enough ships of ID {sid}")

    # Check fuel
    origin_coord = Coordinate(
        galaxy=state["coordinates"]["galaxy"],
        system=state["coordinates"]["system"],
        position=state["coordinates"]["position"]
    )
    target_coord = Coordinate(
        galaxy=req.target.galaxy,
        system=req.target.system,
        position=req.target.position,
        planet_type=PlanetType(req.target.planet_type),
    )
    distance = FlightCalculator.calculate_distance(origin_coord, target_coord)

    min_speed = 999999
    total_fuel = 0
    for sid, count in req.ships.items():
        if count <= 0 or sid not in SHIPS:
            continue
        ship = SHIPS[sid]
        if ship.base_speed < min_speed:
            min_speed = ship.base_speed

    if min_speed == 999999:
        min_speed = 5000

    flight_time = FlightCalculator.calculate_flight_time_seconds(
        distance=distance,
        max_fleet_speed=min_speed,
        speed_percent=req.speed_percent,
        universe_speed_fleet=1.0,
    )

    for sid, count in req.ships.items():
        if count <= 0 or sid not in SHIPS:
            continue
        ship = SHIPS[sid]
        fuel_per_ship = FlightCalculator.calculate_fuel_consumption(
            distance=distance,
            flight_time_seconds=flight_time,
            ship_fuel_usage=ship.fuel_consumption,
            ship_speed=ship.base_speed,
            speed_percent=req.speed_percent,
        )
        total_fuel += fuel_per_ship * count

    if state["resources"]["deuterium"] < total_fuel:
        raise HTTPException(status_code=400, detail="Not enough deuterium for flight fuel.")

    global NEXT_MISSION_ID

    # Deduct ships and fuel
    for sid, count in req.ships.items():
        state["ships"][sid] -= count

    state["resources"]["deuterium"] -= total_fuel

    mission_entry = {
        "id": NEXT_MISSION_ID,
        "origin_planet_id": req.origin_planet_id,
        "mission_type": req.mission_type,
        "target": {
            "galaxy": req.target.galaxy,
            "system": req.target.system,
            "position": req.target.position,
        },
        "ships": req.ships,
        "start_time": time.time(),
        "duration": flight_time,
        "status": "flying",
        "fuel_consumed": total_fuel,
    }
    FLEET_MISSIONS.append(mission_entry)
    NEXT_MISSION_ID += 1

    return FleetSendResponse(
        success=True,
        message=f"함대가 [{req.target.galaxy}:{req.target.system}:{req.target.position}] 목표로 발송되었습니다!",
        flight_time_seconds=flight_time,
        fuel_consumed=total_fuel
    )


