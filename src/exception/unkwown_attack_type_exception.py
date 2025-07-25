class UnknownAttackTypeException(Exception):
    def __init__(self, attack_type):
        self.attack_type:str = attack_type

    def __str__(self):
        return f'{self.attack_type} is not an attack type !'