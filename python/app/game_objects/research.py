from typing import Dict
from python.app.game_objects.models import BuildingObject, GameObjectPrice

RESEARCH: Dict[int, BuildingObject] = {}

RESEARCH[106] = BuildingObject(id=106, machine_name="espionage_technology", title="Espionage Technology", class_name="espionageTechnology", description="Spy tech.", price=GameObjectPrice(metal=200, crystal=1000, deuterium=200, energy=0, factor=2.0))
RESEARCH[108] = BuildingObject(id=108, machine_name="computer_technology", title="Computer Technology", class_name="computerTechnology", description="More fleet slots.", price=GameObjectPrice(metal=0, crystal=400, deuterium=600, energy=0, factor=2.0))
RESEARCH[109] = BuildingObject(id=109, machine_name="weapon_technology", title="Weapon Technology", class_name="weaponTechnology", description="Increase weapon power 10% per level.", price=GameObjectPrice(metal=800, crystal=200, deuterium=0, energy=0, factor=2.0))
RESEARCH[110] = BuildingObject(id=110, machine_name="shield_technology", title="Shield Technology", class_name="shieldTechnology", description="Increase shield power.", price=GameObjectPrice(metal=200, crystal=600, deuterium=0, energy=0, factor=2.0))
RESEARCH[111] = BuildingObject(id=111, machine_name="armour_technology", title="Armour Technology", class_name="armourTechnology", description="Increase hull.", price=GameObjectPrice(metal=1000, crystal=0, deuterium=0, energy=0, factor=2.0))
