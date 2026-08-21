from datetime import datetime
from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, Integer, String, Float, DateTime, ForeignKey, Text

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    dark_matter: Mapped[int] = mapped_column(BigInteger, default=0)
    current_planet_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Planet(Base):
    __tablename__ = "planets"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255), default="Homeworld")
    galaxy: Mapped[int] = mapped_column(Integer, index=True)
    system: Mapped[int] = mapped_column(Integer, index=True)
    position: Mapped[int] = mapped_column(Integer, index=True)
    planet_type: Mapped[int] = mapped_column(Integer, default=1) # 1=planet, 3=moon
    diameter: Mapped[int] = mapped_column(Integer, default=12800)
    field_current: Mapped[int] = mapped_column(Integer, default=0)
    field_max: Mapped[int] = mapped_column(Integer, default=163)
    temp_min: Mapped[int] = mapped_column(Integer, default=-10)
    temp_max: Mapped[int] = mapped_column(Integer, default=30)
    
    # Resources (Float in latest OGameX migration)
    metal: Mapped[float] = mapped_column(Float, default=500.0)
    crystal: Mapped[float] = mapped_column(Float, default=500.0)
    deuterium: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Building Levels
    metal_mine: Mapped[int] = mapped_column(Integer, default=0)
    crystal_mine: Mapped[int] = mapped_column(Integer, default=0)
    deuterium_synthesizer: Mapped[int] = mapped_column(Integer, default=0)
    solar_plant: Mapped[int] = mapped_column(Integer, default=0)
    fusion_plant: Mapped[int] = mapped_column(Integer, default=0)
    solar_satellite: Mapped[int] = mapped_column(Integer, default=0)
    robot_factory: Mapped[int] = mapped_column(Integer, default=0)
    shipyard: Mapped[int] = mapped_column(Integer, default=0)
    research_lab: Mapped[int] = mapped_column(Integer, default=0)
    metal_store: Mapped[int] = mapped_column(Integer, default=0)
    crystal_store: Mapped[int] = mapped_column(Integer, default=0)
    deuterium_store: Mapped[int] = mapped_column(Integer, default=0)

    # Ships
    small_cargo: Mapped[int] = mapped_column(BigInteger, default=0)
    large_cargo: Mapped[int] = mapped_column(BigInteger, default=0)
    light_fighter: Mapped[int] = mapped_column(BigInteger, default=0)
    heavy_fighter: Mapped[int] = mapped_column(BigInteger, default=0)
    cruiser: Mapped[int] = mapped_column(BigInteger, default=0)
    battleship: Mapped[int] = mapped_column(BigInteger, default=0)
    colony_ship: Mapped[int] = mapped_column(BigInteger, default=0)
    recycler: Mapped[int] = mapped_column(BigInteger, default=0)
    espionage_probe: Mapped[int] = mapped_column(BigInteger, default=0)
    bomber: Mapped[int] = mapped_column(BigInteger, default=0)
    destroyer: Mapped[int] = mapped_column(BigInteger, default=0)
    deathstar: Mapped[int] = mapped_column(BigInteger, default=0)
    battlecruiser: Mapped[int] = mapped_column(BigInteger, default=0)
    reaper: Mapped[int] = mapped_column(BigInteger, default=0)
    pathfinder: Mapped[int] = mapped_column(BigInteger, default=0)

    # Defenses
    rocket_launcher: Mapped[int] = mapped_column(BigInteger, default=0)
    laser_cannon_light: Mapped[int] = mapped_column(BigInteger, default=0)
    laser_cannon_heavy: Mapped[int] = mapped_column(BigInteger, default=0)
    gauss_cannon: Mapped[int] = mapped_column(BigInteger, default=0)
    ion_cannon: Mapped[int] = mapped_column(BigInteger, default=0)
    plasma_turret: Mapped[int] = mapped_column(BigInteger, default=0)
    shield_dome_small: Mapped[int] = mapped_column(Integer, default=0)
    shield_dome_large: Mapped[int] = mapped_column(Integer, default=0)
    anti_ballistic_missile: Mapped[int] = mapped_column(Integer, default=0)
    interplanetary_missile: Mapped[int] = mapped_column(Integer, default=0)

    time_last_update: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FleetMission(Base):
    __tablename__ = "fleet_missions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    galaxy_from: Mapped[int] = mapped_column(Integer)
    system_from: Mapped[int] = mapped_column(Integer)
    position_from: Mapped[int] = mapped_column(Integer)
    type_from: Mapped[int] = mapped_column(Integer, default=1)
    
    galaxy_to: Mapped[int] = mapped_column(Integer)
    system_to: Mapped[int] = mapped_column(Integer)
    position_to: Mapped[int] = mapped_column(Integer)
    type_to: Mapped[int] = mapped_column(Integer, default=1)

    mission_type: Mapped[int] = mapped_column(Integer) # 1=Attack, 3=Transport, 4=Deploy, etc.
    time_departure: Mapped[datetime] = mapped_column(DateTime)
    time_arrival: Mapped[datetime] = mapped_column(DateTime, index=True)
    
    metal: Mapped[float] = mapped_column(Float, default=0.0)
    crystal: Mapped[float] = mapped_column(Float, default=0.0)
    deuterium: Mapped[float] = mapped_column(Float, default=0.0)
    deuterium_consumption: Mapped[float] = mapped_column(Float, default=0.0)
    
    processed: Mapped[int] = mapped_column(Integer, default=0, index=True)
    canceled: Mapped[int] = mapped_column(Integer, default=0)
