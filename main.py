import tkinter as tk
from src.simulation import Simulation
import yaml

if __name__ == "__main__":
    with open("config.yml", "r") as f:
        config = yaml.safe_load(f)
    window = tk.Tk()
    sim = Simulation(window, config=config)
    window.mainloop()
