#! /usr/bin/env python3

from abc import ABC, abstractmethod
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class Simulation:
    def __init__(self, seed=None, ants=5, num_rivers=5, x=100, y=100):
        # seed random number generator
        np.random.seed(seed)

        self.width  = x
        self.height = y
        self.fig, self.ax = plt.subplots()

        # initialize grid
        self.grid = np.array([[Dirt(x, y) for y in range(self.height)] for x in range(self.width)])
        # maintain a queue of moves to be made
        self.move_queue = np.array([])

        self.generate_map(ants, num_rivers)

        self.draw()

    def generate_map(self, ants, num_rivers):
        self.generate_rivers(num_rivers)
        self.generate_ants(ants)

    def generate_ants(self, ants):
        # place queen
        while True:
            antx = np.random.randint(0, self.width)
            anty = np.random.randint(0, self.height)
            if(isinstance(self.grid[antx][anty], Dirt)):
                break
        ant = Queen(x=antx, y=anty)
        self.grid[antx][anty] = ant
        # place initial workers
        for _ in range(ants):
            while True:
                antx = np.random.randint(0, self.width)
                anty = np.random.randint(0, self.height)
                if(isinstance(self.grid[antx][anty], Dirt)):
                    break
            ant = Worker(x=antx, y=anty)
            self.grid[antx][anty] = ant

    def generate_river(self, initial_direction=0, direction=0, riverx=0, rivery=0, length=0):
        repeat_count = 0
        # 1 = up
        # 2 = left
        # 3 = down
        # 4 = right
        while True:
            if repeat_count > 20:
                return
            if direction is 0:
                riverx = np.random.randint(0, self.width)
                rivery = np.random.randint(0, self.height)
            elif direction is 1:
                rivery += 1
            elif direction is 2:
                riverx += 1
            elif direction is 3:
                rivery -= 1
            elif direction is 4:
                riverx -= 1
            # check if the tile placement would be invalid
            if riverx >= self.width or riverx < 0 or rivery >= self.height or rivery < 0:
                repeat_count += 1
                continue
            if isinstance(self.grid[riverx][rivery], Water):
                repeat_count += 1
                continue
            break
        self.grid[riverx][rivery] = Water(riverx,rivery)
        # if it's the first tile, pick any direction randomly
        if direction is 0:
            direction = np.random.randint(1,5)
        else:
            # otherwise we want to heavily favor going straight and never go back
            direction_decision = np.random.randint(0,1000)
            if direction_decision < 900:
                direction = initial_direction
            elif direction_decision < 950:
                direction = (initial_direction + 2) % 4 + 1
            else:
                direction = (initial_direction + 4) % 4 + 1
        # randomly cut river short
        # this is an inverse probability as a function of map size
        cutoff = np.random.randint(0, (self.width + self.height) / 2 - length)
        if cutoff < 1:
            return
        if initial_direction is 0:
            initial_direction = direction
        self.generate_river(initial_direction, direction, riverx, rivery, length + 1)

    def generate_rivers(self, num_rivers):
        for _ in range(num_rivers):
            self.generate_river()

    def assign_colors(self):
        try:
            self.colors
        # init colors if they do not exist
        except:
            self.colors = []
            for x, col in enumerate(self.grid):
                self.colors.append([])
                for square in col:
                    self.colors[x].append(square.color())
            return
        # intelligently modify colors
        # TODO: do this using moves

    def draw(self):
        self.assign_colors()
        self.img = self.ax.imshow(self.colors)

    def tick(self, frame_number):
        for col in self.grid:
            for square in col:
                if(isinstance(square, Ant)):
                    square.on_tick()

    def run(self):
        plt.title("pyAnt")
        self.animation = FuncAnimation(self.fig, self.tick, interval=10)
        plt.show()

class Square(ABC):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @abstractmethod
    def walkable(self):
        return True

    @abstractmethod
    def color(self):
        return (0,0,0,1)

    @abstractmethod
    def on_tick(self):
        pass

# Terrains {{{

class Terrain(Square):
    def __init__(self, x, y):
        super().__init__(x, y)

    def on_tick(self):
        pass

class Dirt(Terrain):
    def __init__(self, x, y):
        super().__init__(x, y)

    def walkable(self):
        return True

    def color(self):
        return (0.6, 0.4, 0.2, 1)

class Water(Terrain):
    def __init__(self, x, y):
        super().__init__(x, y)

    def walkable(self):
        return False

    def color(self):
        return (0, 0.6, 1, 1)

# }}}
# Ants {{{

class Ant(Square):
    def __init__(self, x, y):
        super().__init__(x, y)

    def walkable(self):
        return False

    @abstractmethod
    def move(self):
        pass

class Worker(Ant):
    def __init__(self, x, y):
        super().__init__(x, y)

    def color(self):
        return (0, 0.8, 0, 1)

    def on_tick(self):
        # TODO: specify worker AI
        pass

    def move(self):
        # TODO: add move logic
        pass

class Queen(Ant):
    def __init__(self, x, y):
        super().__init__(x, y)

    def color(self):
        return (1, 0, 1, 1)

    def on_tick(self):
        # TODO: specify queen ai
        pass

    def move(self):
        pass

# }}}
