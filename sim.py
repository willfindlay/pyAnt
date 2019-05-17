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

        # create (x by y) fig
        self.fig, self.ax = plt.subplots()
        #self.ax.set_xlim(0, x), self.ax.set_xticks([])
        #self.ax.set_ylim(0, y), self.ax.set_yticks([])

        # initialize grid
        self.grid = np.array([[None for _ in range(x)] for _ in range(y)])
        # maintain a stack of changes in simulation state
        self.state_changes = np.array([])

        # spawn random ants
        # TODO set coordinates of queen randomly
        # TODO set coordinates of workers randomly
        self.ants = []
        for i in range(ants):
            antx = np.random.uniform(0, x)
            anty = np.random.uniform(0, y)
            ant = Worker(x=antx, y=anty)
            self.ants.append(ant)

        self.draw()

    def color_by_obj(self, obj):
        # colors will be of form (r,g,b,a)
        # where r, g, b, and a are all in range [0,1]
        if type(obj) is Queen:
            return (1, 0, 1, 1)
        if type(obj) is Worker:
            return (0, 0.8, 0, 1)
        # dirt tile
        return (0.6, 0.4, 0.2, 1)

    def assign_colors(self):
        try:
            self.colors
        # init colors if they do not exist
        except:
            self.colors = []
            for i, row in enumerate(self.grid):
                self.colors.append([])
                for square in row:
                    self.colors[i].append(self.color_by_obj(square))
            return
        # intelligently modify colors
        for change in self.state_changes:
            x, y = change

    def draw(self):
        self.assign_colors()
        self.img = self.ax.imshow(self.colors)

    def tick(self, frame_number):
        for ant in self.ants:
            ant.on_tick()

    def run(self):
        plt.title("pyAnt")
        self.animation = FuncAnimation(self.fig, self.tick, interval=10)
        plt.show()

class Ant(ABC):
    def __init__(self, x=1, y=1):
        self.x = x
        self.y = y

    @abstractmethod
    def on_tick(self):
        pass

    @abstractmethod
    def move(self):
        pass

class Worker(Ant):
    def __init__(self, x=1, y=1):
        super().__init__(x, y)

    def on_tick(self):
        # TODO: specify worker AI
        pass

    def move(self):
        # TODO: add move logic
        pass

class Queen(Ant):
    def __init__(self, x=1, y=1):
        super().__init__(x, y)

    def on_tick(self):
        # TODO: specify queen ai
        pass

    def move(self):
        pass
