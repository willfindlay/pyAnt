#! /usr/bin/env python3

from abc import ABC, abstractmethod
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class Simulation:
    def __init__(self, seed=None, ants=5, num_rivers=0, x=100, y=100):
        # seed random number generator
        np.random.seed(seed)

        self.width  = x
        self.height = y
        self.fig, self.ax = plt.subplots()

        # initialize grid
        self.grid = np.array([[Dirt(x, y) for y in range(self.height)] for x in range(self.width)])
        # maintain a queue of moves to be made
        self.move_queue = np.array([])

        self.statechanged = False
        self.day = 1
        self.ticks = 0

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
            if(self.grid[antx][anty].walkable()):
                break
        self.queen = Queen(sim = self, num_ants = ants)
        self.grid[antx][anty].set_unit(self.queen)

    def generate_river(self, initial_direction=0, direction=0, riverx=0, rivery=0):
        repeat_count = 0
        length = 0
        # 1 = up
        # 2 = left
        # 3 = down
        # 4 = right
        while True:
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
                if direction_decision < 800:
                    direction = initial_direction
                elif direction_decision < 900:
                    direction = (initial_direction + 2) % 4 + 1
                else:
                    direction = (initial_direction + 4) % 4 + 1
            # randomly cut river short
            # this is an inverse probability as a function of map size
            cutoff = np.random.randint(0, (self.width + self.height) - length)
            if cutoff < 5:
                return
            if initial_direction is 0:
                initial_direction = direction

    def generate_rivers(self, num_rivers):
        for _ in range(num_rivers):
            self.generate_river()

    def assign_colors(self):
        self.colors = []
        for x, col in enumerate(self.grid):
            self.colors.append([])
            for square in col:
                self.colors[x].append(square.color())

    def draw(self):
        self.assign_colors()
        self.img  = self.ax.imshow(self.colors)
        stats = ""
        stats += f"Day: {self.day}\n"
        stats += f"Seed: {np.random.get_state()[1][0]}\n"
        stats += f"Queen Age: {self.queen.age}\n"
        stats += f"Queen Food: {self.queen.hunger * 100}%\n"
        stats += f"Queen Water: {self.queen.thirst * 100}%\n"
        stats += f"Colony Food: {self.queen.food}\n"
        stats += f"Colony Water: {self.queen.water}\n"
        stats += f"Colony Eggs: {self.queen.num_eggs()}\n"
        stats += f"Colony Larvae: {self.queen.num_larvae()}\n"
        stats += f"Colony Workers: {self.queen.num_workers()}\n"
        self.info = self.fig.text(0.05, 0.95, stats, fontsize=14, verticalalignment='top',
                bbox= dict(boxstyle='round', facecolor='wheat'))

    def tick(self, frame_number):
        self.ticks += 1
        if self.ticks % (24 * 36) == 0:
            self.day += 1
            self.queen.age += 1
            self.statechanged = True
        self.queen.on_tick(self)
        for worker in self.queen.workers:
            worker.on_tick(self)
        if self.statechanged:
            self.fig.clf()
            self.fig.add_axes(self.ax)
            self.draw()
        self.statechanged = False

    def run(self):
        plt.title(f"pyAnt")
        self.animation = FuncAnimation(self.fig, self.tick, interval=10)
        plt.show()

# Terrains {{{

class Square(ABC):
    def __init__(self, x, y, obj=None):
        self.x = x
        self.y = y
        self.unit = obj
        self.m_color = (0, 0, 0, 1)
        self.m_walkable = True

    def walkable(self):
        if self.unit is not None:
            return self.unit.walkable()
        return self.m_walkable

    def color(self):
        if self.unit is not None:
            return self.unit.color()
        return self.m_color

    def set_unit(self, unit):
        unit.square = self
        unit.x = self.x
        unit.y = self.y
        self.unit = unit
        return True

    def moved_to(self, unit):
        if self.walkable() is False:
            return False
        if self.unit is not None:
            return self.unit.moved_to()
        if unit.square is not None:
            unit.square.unit = None
        return self.set_unit(unit)

class Dirt(Square):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.m_color = (0.6, 0.4, 0.2, 1)
        self.m_walkable = True

class Water(Square):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.m_color = (0, 0.6, 1, 1)
        self.m_walkable = False

# }}}
# Simulation Objects {{{

class SimulationObject(ABC):
    def __init__(self, sim):
        self.square = None
        self.x = 0
        self.y = 0
        self.sim = sim

    @abstractmethod
    def walkable(self):
        return False

    def adjacent_tiles(self):
        tiles = []
        if self.x + 1 <  self.sim.width:
            tiles.append(self.sim.grid[self.x + 1][self.y])
        if self.x - 1 >= 0:
            tiles.append(self.sim.grid[self.x - 1][self.y])
        if self.y + 1 <  self.sim.height:
            tiles.append(self.sim.grid[self.x][self.y + 1])
        if self.y - 1 >= 0:
            tiles.append(self.sim.grid[self.x][self.y - 1])
        return tiles

    def color(self):
        return self.m_color

class Food(SimulationObject):
    def __init__(self, sim):
        super().__init__(sim)

    def walkable(self):
        return True

class Ant(SimulationObject):
    def __init__(self, sim):
        super().__init__(sim)

    def walkable(self):
        return False

    @abstractmethod
    def on_tick(self, simulation):
        pass

    def move_to(self, tile=None, x=None, y=None):
        result = False
        if tile is not None:
            result = tile.moved_to(self)
        else:
            result = self.sim.grid[x][y].moved_to(self)
        if result is True:
            self.sim.statechanged = True

class Worker(Ant):
    def __init__(self, sim):
        super().__init__(sim)
        self.m_color = (0, 0.8, 0, 1)
        self.job = "rest"

    def on_tick(self, simulation):
        if self.job is "rest":
            pass
        elif self.job is "search":
            tiles = []
            for tile in self.adjacent_tiles():
                if tile.walkable():
                    tiles.append(tile)
            choice = np.random.randint(0,len(tiles))
            self.walk(tiles[choice])

    def walk(self, tile):
        return self.move_to(tile)

    def leave_pheromones(self, pheromone):
        pass


class Queen(Ant):
    def __init__(self, sim, num_ants):
        super().__init__(sim)
        self.m_color = (1, 0, 1, 1)
        self.age = 0
        self.hunger = 1
        self.thirst = 1
        self.food = 0
        self.water = 0
        self.larvae = []
        self.eggs = []
        self.workers = []

        for _ in range(num_ants):
            self.workers.append(Worker(self.sim))

    def on_tick(self, simulation):
        # TODO: specify queen ai
        self.dispatch_worker("search")

    def num_workers(self):
        return len(self.workers)

    def num_eggs(self):
        return len(self.eggs)

    def num_larvae(self):
        return len(self.larvae)

    def dispatch_worker(self, job):
        # find an empty tile to poop out a worker
        the_tile = None
        for tile in self.adjacent_tiles():
            if tile.unit is None:
                the_tile = tile
        if the_tile is None:
            return
        for worker in self.workers:
            if worker.job is "rest":
                worker.move_to(the_tile)
                worker.job = job
                return

# }}}
