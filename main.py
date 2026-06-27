import tkinter as tk
from src.simulation import Simulation

if __name__ == "__main__":
    window = tk.Tk()
    sim = Simulation(window, agent_size=12, screen_width=800, screen_height=600)
    window.mainloop()
