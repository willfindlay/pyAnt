#! /usr/bin/env python3

from abc import ABC, abstractmethod
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class Simulation:
    def __init__(self, seed=None, ants=5, x=100, y=100):
        # seed random number generator
        np.random.seed(seed)

        self.width  = x
        self.height = y
        self.fig, self.ax = plt.subplots()

        # initialize grid
        self.grid = np.array([[Dirt(x, y) for y in range(self.height)] for x in range(self.width)])
        # maintain a queue of moves to be made
        self.move_queue = np.array([])

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

        self.draw()

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
