class Weapon:
    def __init__(self, name, damage, cost=0):
        self.name = name
        self.damage = damage
        self.cost = cost


DEFAULT_WEAPONS = [
    Weapon('Sword', 25, cost=0),
    Weapon('Axe', 40, cost=100),
    Weapon('Gun', 50, cost=200),
]
