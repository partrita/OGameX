from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from python.app.models.entities import Planet, User
from python.app.services.resource_calculator import ResourceCalculator
from python.app.game_objects.buildings import calculate_building_storage

class PlanetService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_planet_by_id(self, planet_id: int) -> Optional[Planet]:
        stmt = select(Planet).where(Planet.id == planet_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_planet_resources(self, planet: Planet, economy_speed: float = 1.0) -> Planet:
        """Calculates elapsed time since last update and updates stored resource balances."""
        now = datetime.utcnow()
        elapsed_seconds = (now - planet.time_last_update).total_seconds()
        
        if elapsed_seconds <= 0:
            return planet

        hourly = ResourceCalculator.calculate_hourly_production(
            metal_mine_level=planet.metal_mine,
            crystal_mine_level=planet.crystal_mine,
            deuterium_synth_level=planet.deuterium_synthesizer,
            solar_plant_level=planet.solar_plant,
            max_temp=planet.temp_max,
            economy_speed=economy_speed,
        )

        storages = {
            "metal": calculate_building_storage(planet.metal_store),
            "crystal": calculate_building_storage(planet.crystal_store),
            "deuterium": calculate_building_storage(planet.deuterium_store),
        }

        current_res = {
            "metal": planet.metal,
            "crystal": planet.crystal,
            "deuterium": planet.deuterium,
        }

        updated_res = ResourceCalculator.update_resources_for_elapsed_time(
            current_resources=current_res,
            hourly_production=hourly,
            elapsed_seconds=elapsed_seconds,
            storages=storages,
        )

        planet.metal = updated_res["metal"]
        planet.crystal = updated_res["crystal"]
        planet.deuterium = updated_res["deuterium"]
        planet.time_last_update = now

        await self.db.commit()
        await self.db.refresh(planet)
        return planet
