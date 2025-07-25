from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from models.attack_models import AttackModelOutShort
from models.statistics import Statistics


class TypePokemon(str, Enum):
    attacker = "Attacker"
    defender = "Defender"
    allRounder = "All-Rounder"
    speedster = "Speedster"
    supporter = "Supporter"

class PokemonModelIn(BaseModel):
    """
    The output model.
    """
    name: str
    pokemon_type: TypePokemon
    level: int
    statistics : Statistics
    url_image:str

    class Config:
        arbitrary_types_allowed = True


class PokemonModelShort(BaseModel):
    """
    The output model.
    """
    name: str
    id:  int
    pokemon_type: Optional[str] = None
    url_image: Optional[str] = None
    url:Optional[str] = None


class PokemonModelFull(BaseModel):
    """
    The output model.
    """
    name: str
    id:  int
    pokemon_type: Optional[str] = None
    level : int
    statistic : Statistics
    attacks : List[AttackModelOutShort]
    url_image: Optional[str] = None
    url:Optional[str] = None

    class Config:
        arbitrary_types_allowed = True