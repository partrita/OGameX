from typing import Dict
from python.app.game_objects.models import ShipObject, GameObjectPrice

DEFENSES: Dict[int, ShipObject] = {}

DEFENSES[401] = ShipObject(
    id=401, machine_name="rocket_launcher", title="Rocket Launcher",
    class_name="rocketLauncher", description="Simple ground defense.",
    price=GameObjectPrice(metal=2000, crystal=0, deuterium=0, energy=0),
    structural_integrity=2000, shield_power=20, weapon_power=80,
    cargo_capacity=0, base_speed=0, fuel_consumption=0,
)
DEFENSES[402] = ShipObject(
    id=402, machine_name="laser_cannon_light", title="Light Laser",
    class_name="lightLaser", description="Light laser cannon.",
    price=GameObjectPrice(metal=1500, crystal=500, deuterium=0, energy=0),
    structural_integrity=2000, shield_power=25, weapon_power=100,
    cargo_capacity=0, base_speed=0, fuel_consumption=0,
)
DEFENSES[403] = ShipObject(
    id=403, machine_name="laser_cannon_heavy", title="Heavy Laser",
    class_name="heavyLaser", description="Heavy laser cannon.",
    price=GameObjectPrice(metal=6000, crystal=2000, deuterium=0, energy=0),
    structural_integrity=8000, shield_power=100, weapon_power=250,
    cargo_capacity=0, base_speed=0, fuel_consumption=0,
)
DEFENSES[404] = ShipObject(
    id=404, machine_name="gauss_cannon", title="Gauss Cannon",
    class_name="gaussCannon", description="Gauss cannon.",
    price=GameObjectPrice(metal=20000, crystal=15000, deuterium=2000, energy=0),
    structural_integrity=35000, shield_power=200, weapon_power=1100,
    cargo_capacity=0, base_speed=0, fuel_consumption=0,
)
