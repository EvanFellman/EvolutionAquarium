import argparse

parser = argparse.ArgumentParser(description="A fun aquarium experiment")
parser.add_argument("--highlight-witnessed", action='store_true', help='Any food that is visible by any agent will be highlighted')
parser.add_argument("--load-prev-nets", action="store_true", help="Load previously pretrained agent models")
parser.add_argument("--trail", action="store_true", help="Show agents' paths")
args = parser.parse_args()

import tkinter as tk
from src.simulation import Simulation
import yaml


if __name__ == "__main__":
    with open("config.yml", "r") as f:
        config = yaml.safe_load(f)
    window = tk.Tk()
    sim = Simulation(window, config=config, args=args)
    window.mainloop()
