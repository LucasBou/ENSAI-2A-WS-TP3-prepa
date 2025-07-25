from pydantic.main import BaseModel


class Statistics(BaseModel):
    hp: int
    attack: int
    defense: int
    spe_atk: int
    spe_def: int
    speed: int
