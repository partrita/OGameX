import math
from typing import Dict
from python.app.game_objects.models import ShipObject, GameObjectPrice

SHIPS: Dict[int, ShipObject] = {}

# Small Cargo (ID 202)
SHIPS[202] = ShipObject(
    id=202,
    machine_name="small_cargo",
    title="Small Cargo",
    class_name="smallCargo",
    description="The small cargo is an agile ship that can quickly transport resources.",
    price=GameObjectPrice(metal=2000, crystal=2000, deuterium=0, energy=0),
    structural_integrity=4000,
    shield_power=10,
    weapon_power=5,
    cargo_capacity=5000,
    base_speed=5000,
    fuel_consumption=10,
    rapidfire={210: 5, 212: 5} # Solar Satellite, Espionage Probe
)

# Large Cargo (ID 203)
SHIPS[203] = ShipObject(
    id=203,
    machine_name="large_cargo",
    title="Large Cargo",
    class_name="largeCargo",
    description="The large cargo has a significantly improved cargo hold.",
    price=GameObjectPrice(metal=6000, crystal=6000, deuterium=0, energy=0),
    structural_integrity=12000,
    shield_power=25,
    weapon_power=5,
    cargo_capacity=25000,
    base_speed=7500,
    fuel_consumption=50,
    rapidfire={210: 5, 212: 5}
)

# Light Fighter (ID 204)
SHIPS[204] = ShipObject(
    id=204,
    machine_name="light_fighter",
    title="Light Fighter",
    class_name="lightFighter",
    description="This is the first ship every emperor builds.",
    price=GameObjectPrice(metal=3000, crystal=1000, deuterium=0, energy=0),
    structural_integrity=4000,
    shield_power=10,
    weapon_power=50,
    cargo_capacity=50,
    base_speed=12500,
    fuel_consumption=20,
    rapidfire={210: 5, 212: 5}
)

# Cruiser (ID 206)
SHIPS[206] = ShipObject(
    id=206,
    machine_name="cruiser",
    title="Cruiser",
    class_name="cruiser",
    description="Cruisers are fast and heavily armed against light fighters and rocket launchers.",
    price=GameObjectPrice(metal=20000, crystal=7000, deuterium=2000, energy=0),
    structural_integrity=27000,
    shield_power=50,
    weapon_power=400,
    cargo_capacity=800,
    base_speed=15000,
    fuel_consumption=300,
    rapidfire={204: 6, 210: 5, 212: 5, 401: 10} # Rocket launcher rapidfire
)

# Battleship (ID 207)
SHIPS[207] = ShipObject(
    id=207,
    machine_name="battleship",
    title="Battleship",
    class_name="battleship",
    description="Battleships form the backbone of any offensive fleet.",
    price=GameObjectPrice(metal=45000, crystal=15000, deuterium=0, energy=0),
    structural_integrity=60000,
    shield_power=200,
    weapon_power=1000,
    cargo_capacity=1500,
    base_speed=10000,
    fuel_consumption=500,
    rapidfire={210: 5, 212: 5}
)

# Deathstar (ID 214)
SHIPS[214] = ShipObject(
    id=214,
    machine_name="deathstar",
    title="Deathstar",
    class_name="deathstar",
    description="The power of the Deathstar is unmatched.",
    price=GameObjectPrice(metal=5000000, crystal=4000000, deuterium=1000000, energy=0),
    structural_integrity=9000000,
    shield_power=50000,
    weapon_power=200000,
    cargo_capacity=1000000,
    base_speed=100,
    fuel_consumption=1,
    rapidfire={202: 250, 203: 250, 204: 200, 206: 100, 207: 30}
)
