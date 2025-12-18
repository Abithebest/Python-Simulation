import random;

from utils import Colors;

def classify_terrain(t, x, y):
    if t < 0.30:
        return Water(x, y)
    elif t < 0.40:
        return Sand(x, y)
    elif t < 0.65 and t > 0.60 and random.randint(0, 100) > 60:
        return Bush(x, y)
    else:
        return Grass(x, y)

class Grass:
    def __init__(self, x, y):
        self.symbol = f'{Colors.GRASS}.{Colors.ENDC}'
        self.current_symbol = self.symbol
        self.type = "grass"
        self.walkable = True
        self.cordinate = (x, y)

    def VisionInteraction(self, agent, world):
        agent.memory.add_value(self.cordinate, 'tile', self.type)
        return True
    
    def StepInteraction(self, agent, world):
        return True
    
class Sand:
    def __init__(self, x, y):
        self.symbol = f'{Colors.SAND}.{Colors.ENDC}'
        self.current_symbol = self.symbol
        self.type = "sand"
        self.walkable = True
        self.cordinate = (x, y)

    def VisionInteraction(self, agent, world):
        agent.memory.add_value(self.cordinate, 'tile', self.type)
        return True
    
    def StepInteraction(self, agent, world):
        return True

class Water:
    def __init__(self, x, y):
        self.symbol = f'{Colors.WATER}~{Colors.ENDC}'
        self.current_symbol = self.symbol
        self.type = "water"
        self.walkable = False
        self.cordinate = (x, y)

    def VisionInteraction(self, agent, world):
        agent.memory.add_value(self.cordinate, 'water')
        return True
    
    def StepInteraction(self, agent, world):
        agent.drink()
        return True

class Bush:
    def __init__(self, x, y):
        self.symbol = f'{Colors.GRASS_FOOD}.{Colors.ENDC}'
        self.current_symbol = self.symbol
        self.type = "food"
        self.walkable = True
        self.cordinate = (x, y)

    def VisionInteraction(self, agent, world):
        agent.memory.add_value(self.cordinate, 'food')
        return True
    
    def StepInteraction(self, agent, world):
        agent.eat()
        return True

class Tree:
    def __init__(self, x, y):
        self.symbol = f'{Colors.TREE}T{Colors.ENDC}'
        self.current_symbol = self.symbol
        self.type = "tree"
        self.walkable = False
        self.cordinate = (x, y)

    def VisionInteraction(self, agent, world):
        return True
    
    def StepInteraction(self, agent, world):
        return True
