import random;
import string;
import time;
import matplotlib.pyplot as plt;
import os;
import noise;
import numpy as np;
import copy;

from config import *;
from utils import *;
from pathfind import *;
from memory import *;
from terrain import classify_terrain;

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
        self.facing = (0, 1)
        self.hunger = 0
        self.thirst = 0
        self.health = 100
        self.age = {
            "steps": random.randint(10, 500),
            "max_steps": random.randint(800, 1500)
        }
        self.memory = Memory(self)
        self.config = {
            "forget_value": 5
        }

        if self.age['steps'] >= 180:
            self.name = f"Agent.{random.choice(string.ascii_uppercase)}"
        else:
            self.name = f"Agent.{random.choice(string.ascii_lowercase)}"

    def to_dict(self):
        return {
            "name": self.name,
            "hunger": self.hunger,
            "thirst": self.thirst,
            "health": self.health,
            "memory": self.memory.to_dict()
        }
    
    def think(self):
        if self.hunger > 50 and len(self.memory.get_value('food')) > 0:
            self.memory.set_value('thought', 'food')
        elif self.thirst > 50 and len(self.memory.get_value('water')) > 0:
            self.memory.set_value('thought', 'water')
        else:
            self.memory.set_value('thought', None)

        world.pathfind(self)

    def move(self):
        path = self.memory.get_value('pathfind')

        if len(path) <= 0:
            path = world.pathfind(self)

        if path:
            dx, dy = path[0]

            if len(path) == 1:
                self.memory.set_value('pathfind', [])
            else:
                del path[0]
        else:
            dx, dy = (0, 0)


        self.x += dx
        self.y += dy
        self.facing = (dx, dy)

    def eat(self):
        if self.memory.get_value('thought') == 'food':
            self.hunger = 0
            self.memory.set_value('thought', None)
            #self.hunger = max(0, self.hunger - 30)

    def drink(self):
        if self.memory.get_value('thought') == 'water':
            self.thirst = 0
            self.memory.set_value('thought', None)
            #self.thirst = max(0, self.thirst - 30)

    def update(self):
        self.hunger += random.randint(0,5)
        self.thirst += random.randint(0,5)
        self.age['steps'] += 1

        if self.age['steps'] > 900:
            self.config['forget_value'] = 2
        elif self.age['steps'] > 700:
            self.config['forget_value'] = 3
        elif self.age['steps'] > 500:
            self.config['forget_value'] = 4

        if self.hunger > 80:
            self.health -= 1
        if self.thirst > 80:
            self.health -= 1
        if self.age['steps'] >= self.age['max_steps']:
            self.health = 0

        if self.health <= 0:
            self.die()

    def die(self):
        self.health = 0

class World:
    def __init__(self, width, height, num_agents):
        self.steps = 0
        self.width = width
        self.height = height
        self.num_agents = num_agents
        self.agents = False
        self.agent_terrains = []
        self.world = np.zeros((width, height))

    def walkable_spawn(self, width, height):
        while True:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            if self.original_map[y][x].walkable:
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
            [classify_terrain(self.world[y][x], x, y) for x in range(self.width)]
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

                world_map = [[cell.symbol for cell in row] for row in self.original_map]
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

                #append_json(json_file, data)
                break

            self.step()
            time.sleep(0.2)

    def step(self):
        self.steps += 1
        for terrain in self.agent_terrains:
            terrain.current_symbol = terrain.symbol

        for agent in self.agents:
            if agent.health > 0:
                agent.update()
                agent.think()
                if len(agent.memory.get_value('pathfind')) <= 0: self.pathfind(agent)
                agent.move()
                self.update_vision(agent)
                self.check_resources(agent)

                terrain = self.original_map[agent.y][agent.x]
                self.agent_terrains.append(terrain)

                terrain.current_symbol = agent.name.split('.')[1]
        
        self.display_map([[cell.current_symbol for cell in row] for row in self.original_map])

    def pathfind(self, agent):
        target = None
        if agent.memory.get_value('thought') == 'food':
            target = random.choice(agent.memory.get_value('food'))
        if agent.memory.get_value('thought') == 'water':
            target = random.choice(agent.memory.get_value('water'))

        path = self.Pathfinder.find_path((agent.x, agent.y), target or None)

        agent.memory.set_value('pathfind', path)
        return path
            
    def display_map(self, world_map):
        os.system('cls' if os.name == 'nt' else 'clear')

        for row in world_map:
            print(' '.join(row))

        print("-" * 40)

        for agent in self.agents:
            agent_color = Colors.GREEN

            if agent.health <= 0:
                if agent.age['steps'] >= agent.age['max_steps']:
                    agent_color = Colors.AGE_DEATH
                elif agent.thirst > agent.hunger:
                    agent_color = Colors.BLUE
                else:
                    agent_color = Colors.RED

            print(f"{agent_color}{agent.name}{Colors.ENDC} ({agent.x},{agent.y}) | Age: {agent.age['steps']} | Hunger: {agent.hunger} | Thirst: {agent.thirst} | Health: {agent.health} | Memory: {agent.memory.to_dict()}")

    def update_vision(self, agent):
        ax, ay = agent.x, agent.y
        dx, dy = agent.facing

        if (dx, dy) == (0, 0):
            return []
        
        px, py = -dy, dx
        tiles = []
        for offset in (-1, 0, 1):
            vx = ax + dx + px * offset
            vy = ay + dy + py * offset

            if 0 <= vx < self.width and 0 <= vy < self.height:
                tiles.append((vx, vy))
                self.original_map[vy][vx].VisionInteraction(agent, self)

        return tiles

    def check_resources(self, agent):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = agent.x + dx, agent.y + dy

                if 0 <= nx < self.width and 0 <= ny < self.height:
                    self.original_map[ny][nx].StepInteraction(agent, self)

world = World(20, 20, 1)

world.run()