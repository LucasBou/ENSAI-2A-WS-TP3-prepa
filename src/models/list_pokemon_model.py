from typing import List

from pydantic import BaseModel

from models.pokemon_model import PokemonModelShort


class ListPokemonModel(BaseModel):
    count: int
    results: List[PokemonModelShort]

