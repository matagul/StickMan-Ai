class Item:
    def __init__(self, name, effect, duration=0, cost=0):
        self.name = name
        self.effect = effect
        self.duration = duration
        self.cost = cost


HEALTH_PACK = Item('Health', effect='heal', duration=0, cost=50)
ARMOR = Item('Armor', effect='armor', duration=10, cost=75)
INVINCIBILITY = Item('Invincibility', effect='invincible', duration=5, cost=150)
