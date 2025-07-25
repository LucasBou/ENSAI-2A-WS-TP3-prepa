from enum import Enum


class TypeAttackNameModel(str, Enum):
    physical = "physical attack"
    special = "special attack"
    fixed = "fixed damage"
    status = "status attack"
