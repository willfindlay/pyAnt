#! /usr/bin/env python3

from sim import Simulation

if __name__ == "__main__":

    sim = Simulation(ants=5, x=100, y=100, num_rivers=20)

    sim.run()
