class Memory:
    def __init__(self, agent):
        self.agent = agent
        self.known = {
            "Pathfind": [],
            "Thought": None,
            "Tiles": {},
            "Food": [],
            "Water": []
        }

    def to_dict(self):
        return {
            "Tiles": self.known['Tiles'],
            "Thought": self.known['Thought'],
            "Pathfind": self.known['Pathfind'],
            "Food": self.known['Food'],
            "Water": self.known['Water']
        }
    
    def set_value(self, type, value):
        if type == 'pathfind':
            self.known['Pathfind'] = value
        elif type == 'thought':
            self.known['Thought'] = value

    def add_value(self, coord, type, extra=''):
        if type == 'food' and coord not in self.known['Food']:
            if len(self.known['Food']) >= self.agent.config['forget_value']:
                del self.known['Food'][0]

            self.known['Food'].append(coord)
        elif type == 'water' and coord not in self.known['Water']:
            if len(self.known['Water']) >= self.agent.config['forget_value']:
                del self.known['Water'][0]

            self.known['Water'].append(coord)
        elif type == 'tile' and coord not in self.known['Tiles']:
            if len(self.known['Tiles']) >= self.agent.config['forget_value'] * 3:
                self.known['Tiles'].pop(0)

            self.known['Tiles'][coord] = extra
        else:
            pass

    def get_value(self, type):
        if type == 'food':
            return self.known['Food']
        elif type == 'water':
            return self.known['Water']
        elif type == 'tiles':
            return self.known['Tiles']
        elif type == 'pathfind':
            return self.known['Pathfind']
        elif type == 'thought':
            return self.known['Thought']
        else:
            return []
