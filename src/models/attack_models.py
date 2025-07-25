from typing import Optional

from pydantic import BaseModel

from models.type_attack_name_model import TypeAttackNameModel


class AttackModelOut(BaseModel):
    """
    The output model.
    """
    name: str
    id: int
    attack_type: str
    power: Optional[int] = None
    accuracy: Optional[int] = None
    element: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None


class AttackModelIn(BaseModel):
    """
    The output model.
    """
    name: str
    id: int
    attack_type: TypeAttackNameModel
    power: Optional[int] = None
    accuracy: Optional[int] = None
    element: Optional[str] = None
    description: Optional[str] = None


class AttackModelOutShort(BaseModel):
    """
    The output model.
    """
    name: str
    id: int
    attack_type: str
    url: Optional[str] = None
