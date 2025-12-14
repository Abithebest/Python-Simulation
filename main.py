import random;
import time;
import matplotlib.pyplot as plt;
import os;
import noise;
import numpy as np;
import copy;

from utils import *;
from pathfind import *;

start_time = time.perf_counter()
def end_time():
    end_time = time.perf_counter()
    duration = end_time - start_time

    print(f"{Colors.GREEN}DURATION: {duration:.4f}s{Colors.ENDC}")
    return duration

class Agent: 
    def __init__(self, x, y):
        self.y = y
        self.x = x
        self.name = f"Agent.{random.randint(0, 999)}"
        self.hunger = 0
        self.thirst = 0
        self.health = 100
        self.memory = {
            "pathfind": [],
            "thought": None,
            "food": [],
            "water": []
        }

    def to_dict(self):
        return {
            "name": self.name,
            "hunger": self.hunger,
            "thirst": self.thirst,
            "health": self.health,
            "memory": {
                "thought": self.memory['thought'],
                "food": self.memory['food'],
                "water": self.memory['water']
            }
        }
    
    def think(self):
        if self.hunger > 50 and self.memory['food']:
            self.memory['thought'] = 'food'
        elif self.thirst > 50 and self.memory['water']:
            self.memory['thought'] = 'water'
        else:
            self.memory['thought'] = None

        world.pathfind(self)

    def move(self):
        path = self.memory.get('pathfind')

        if not path:
            path = world.pathfind(self)

        if path:
            dx, dy = path[0]

            if len(path) == 1:
                self.memory['pathfind'] = []
            else:
                del path[0]
        else:
            dx, dy = (0, 0)

        self.x += dx
        self.y += dy

    def add_memory(self, cordinate, type):
        if type == 'food' and cordinate not in self.memory['food']:
            self.memory['food'].append(cordinate)
        
        if type == 'water' and cordinate not in self.memory['water']:
            self.memory['water'].append(cordinate)

    def eat(self):
        if self.memory['thought'] == 'food':
            self.hunger = 0
            self.memory['thought'] = None
            #self.hunger = max(0, self.hunger - 30)

    def drink(self):
        if self.memory['thought'] == 'water':
            self.thirst = 0
            self.memory['thought'] = None
            #self.thirst = max(0, self.thirst - 30)

    def update(self):
        self.hunger += random.randint(0,5)
        self.thirst += random.randint(0,5)

        if self.hunger > 80:
            self.health -= 1
        if self.thirst > 80:
            self.health -= 1

        if self.health <= 0:
            self.die()

    def die(self):
        cause = "Health"
        if self.hunger >= 100:
            cause = "Hunger"
        if self.thirst >= 100:
            cause = "Thirst"

        print(f"{self.name} has died due to {cause}.")

class World:
    def __init__(self, width, height, num_agents):
        self.width = width
        self.height = height
        self.num_agents = num_agents
        self.agents = False
        self.world = np.zeros((width, height))

    def walkable_spawn(self, width, height):
        while True:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            if self.original_map[y][x][1]['walkable']:
                return x, y

    def generate_perlin(self):
        scale = 0.06

        ox = random.uniform(0, 1000)
        oy = random.uniform(0, 1000)

        for x in range(self.width):
            for y in range(self.height):
                self.world[y, x] = noise.pnoise2(
                    (x + ox) * scale,
                    (y + oy) * scale
                )
        
        self.world = (self.world - self.world.min()) / (self.world.max() - self.world.min())
        self.original_map = [
            [classify_terrain(self.world[y][x]) for x in range(self.width)]
            for y in range(self.height)
        ]
        self.Pathfinder = Pathfinder(self.original_map, self.width, self.height)

    def run(self):
        self.generate_perlin()
        self.agents = [
            Agent(*self.walkable_spawn(self.width, self.height))
            for _ in range(self.num_agents)
        ]

        while True:
            if all(agent.health <= 0 for agent in self.agents):
                print("All agents have died. Simulation ending.")
                timed = end_time()

                world_map = [[cell[0] for cell in row] for row in self.original_map]
                for row in world_map:
                    map = ' '.join(row)

                data = {
                    "time": timed,
                    "agents": [agent.to_dict() for agent in self.agents],
                    "world": {
                        "width": self.width,
                        "height": self.height,
                        "map": map
                    }
                }

                append_json(json_file, data)
                break

            self.step()
            time.sleep(0.2)

    def step(self):
        world_map = copy.deepcopy(self.original_map)

        for agent in self.agents:
            if agent.health > 0:
                agent.update()
                agent.think()
                if len(agent.memory['pathfind']) <= 0: self.pathfind(agent)
                agent.move()
                self.check_resources(agent)

                world_map[agent.y][agent.x] = 'A'
        
        self.display_map([[cell[0] for cell in row] for row in world_map])

    def pathfind(self, agent):
        target = None
        if agent.memory['thought'] == 'food':
            target = random.choice(agent.memory['food'])
        if agent.memory['thought'] == 'water':
            target = random.choice(agent.memory['water'])

        path = self.Pathfinder.find_path((agent.x, agent.y), target or None)

        agent.memory['pathfind'] = path
        return path
            
    def display_map(self, world_map):
        os.system('cls' if os.name == 'nt' else 'clear')

        for row in world_map:
            print(' '.join(row))

        print("-" * 40)

        for agent in self.agents:
            agent_color = Colors.GREEN

            if agent.health <= 0:
                if agent.thirst > agent.hunger:
                    agent_color = Colors.BLUE
                else:
                    agent_color = Colors.RED

            print(f"{agent_color}{agent.name}{Colors.ENDC} ({agent.x},{agent.y}) | Hunger: {agent.hunger} | Thirst: {agent.thirst} | Health: {agent.health} | Memory: {agent.memory}")

    def check_resources(self, agent):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = agent.x + dx, agent.y + dy

                if 0 <= nx < self.width and 0 <= ny < self.height:
                    type = self.original_map[ny][nx][1]['type']

                    if type == 'food':
                        agent.add_memory((nx, ny), 'food')
                        agent.eat()
                    if(type == 'water'):
                        agent.add_memory((nx, ny), 'water')
                        agent.drink()

world = World(20, 20, 10)

world.run()