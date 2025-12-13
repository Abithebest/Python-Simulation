import random;
import time;
import matplotlib.pyplot as plt;
import os;

from utils import *;

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
            "food": set(),
            "water": set()
        }

    def to_dict(self):
        return {
            "name": self.name,
            "hunger": self.hunger,
            "thirst": self.thirst,
            "health": self.health,
            "memory": {
                "food": list(self.memory['food']),
                "water": list(self.memory['water'])
            }
        }
        
    def move(self, width, height):
        if self.memory['food'] and self.hunger > 50:
            target = random.choice(list(self.memory["food"]))
            self.move_toward(target)
        elif self.memory['water'] and self.thirst > 50:
            target = random.choice(list(self.memory["water"]))
            self.move_toward(target)
        else:
            self.x += random.choice([-1, 1])
            self.y += random.choice([-1, 1])

        self.x = max(0, min(self.x, width - 1))
        self.y = max(0, min(self.y, height - 1))

    def move_toward(self, target):
        target_x, target_y = target

        if self.x < target_x:
            self.x += 1
        elif self.x > target_x:
            self.x -= 1

        if self.y < target_y:
            self.y += 1
        elif self.y > target_y:
            self.y -= 1

    def eat(self):
        self.hunger = max(0, self.hunger - 30)

    def drink(self):
        self.thirst = max(0, self.thirst - 30)

    def update(self):
        self.hunger += random.randint(0,5)
        self.thirst += random.randint(0,5)

        if self.hunger > 80:
            self.health -= 1
        if self.thirst > 80:
            self.health -= 1

        if self.health <= 0:
            self.die()

    def scan_area(self, world):
        food_found = self.memory['food']
        water_found = self.memory['water']

        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = self.x + dx, self.y + dy

                if 0 <= nx < world.width and 0 <= ny < world.height:
                    if (nx, ny) in world.food_sources:
                        food_found.add((nx, ny))
                    if (nx, ny) in world.water_sources:
                        water_found.add((nx, ny))
        
        self.memory['food'] = food_found
        self.memory['water'] = water_found

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
        self.agents = [Agent(random.randint(0, width-1), random.randint(0, height-1)) for _ in range(num_agents)]
        self.food_sources = [(random.randint(0, width-1), random.randint(0, height-1)) for _ in range(5)]
        self.water_sources = [(random.randint(0, width-1), random.randint(0, height-1)) for _ in range(5)]

        print(self.food_sources)
        print(self.water_sources)

    def run(self):
        while True:
            if all(agent.health <= 0 for agent in self.agents):
                print("All agents have died. Simulation ending.")
                time = end_time()

                data = {
                    "time": time,
                    "agents": [agent.to_dict() for agent in self.agents],
                    "world": {
                        "width": self.width,
                        "height": self.height,
                        "food_sources": self.food_sources,
                        "water_sources": self.water_sources
                    }
                }

                append_json(json_file, data)
                break

            self.step()

            time.sleep(1)

    def step(self):
        world_map = [['.' for _ in range(self.width)] for _ in range(self.height)]

        for food in self.food_sources:
            world_map[food[1]][food[0]] = 'F'
        for water in self.water_sources:
            world_map[water[1]][water[0]] = 'W'

        for agent in self.agents:
            if agent.health > 0:
                agent.update()
                agent.move(self.width, self.height)
                self.check_resources(agent)
                agent.scan_area(self)
                
                world_map[agent.y][agent.x] = 'A'

        self.display_map(world_map)
            
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

            print(f"{agent_color}{agent.name}{Colors.ENDC} | Hunger: {agent.hunger} | Thirst: {agent.thirst} | Health: {agent.health} | Memory: {agent.memory}")

    def check_resources(self, agent):
        if (agent.x, agent.y) in self.food_sources:
            agent.eat()
        if (agent.x, agent.y) in self.water_sources:
            agent.drink()

world = World(20, 20, 10)

world.run()