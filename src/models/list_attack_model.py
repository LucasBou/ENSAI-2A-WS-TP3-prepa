from typing import List

from pydantic import BaseModel

from models.attack_models import AttackModelOutShort


class ListAttackModel(BaseModel):
    count: int
    results: List[AttackModelOutShort]
