import tkinter as tk
import math
from src.agent.agent import Agent
import random

class Simulation:
    def __init__(self, root, config: dict):
        self.root = root
        self.root.title("2D Agent Food Simulation")

        self.config = config
        self.trail = []

        # Setup Canvas
        self.canvas = tk.Canvas(root, width=config['Simulation']['screen_width'], height=config['Simulation']['screen_height'], bg="#222222")
        self.canvas.pack()

        # Initialize entities
        self.agents = [Agent(config=config) for _ in range(config['Simulation']['num_agents'])]
        self.foods = [[random.uniform(20, config['Simulation']['screen_width']-20), random.uniform(20, config['Simulation']['screen_height']-20)] for _ in range(config['Simulation']['num_food'])]
        
        for a in self.agents:
            a.pretrain()

        # Start the loop
        self.run_loop()

    def run_loop(self):
        # Clear previous canvas frames
        self.canvas.delete("all")
        
        # 1. Update and Draw Food (Squares)
        for i, food in enumerate(self.foods):
            fx, fy = food
            self.canvas.create_rectangle(
                fx - self.config['Food']['size']/2, fy - self.config['Food']['size']/2,
                fx + self.config['Food']['size']/2, fy + self.config['Food']['size']/2,
                fill="#4CAF50", outline=""
            )
            
        # 1.5 dead and new agents
        dead_agents = []
        new_agents = []

        # 2. Update and Draw Agents (Triangles)
        for agent_id, agent in enumerate(self.agents):
            agent.update(self.foods)
            self.trail.append((agent.x, agent.y))
            if len(self.trail) > 100:
                self.trail = self.trail[-100:] 
            if agent.is_dead():
                dead_agents.append(agent_id)
            # Check collisions with any food item
            for i, food in enumerate(self.foods):
                if math.hypot(agent.x - food[0], agent.y - food[1]) < (self.config['Agent']['size'] + self.config['Agent']['size']) / 2:
                    # Eat food and respawn it elsewhere
                    self.foods[i] = [random.uniform(20, self.config['Simulation']['screen_width']-20), random.uniform(20, self.config['Simulation']['screen_height']-20)]
                    agent.food += self.config['Agent']['eat_amount']
            # Draw oriented triangle geometry
            coords = agent.get_triangle_coords()
            self.canvas.create_polygon(coords, fill="#00BCD4", outline="#FFFFFF")
            
            for f in agent.highlights:
                self.canvas.create_rectangle(f[0]-(self.config['Food']['size']/2), f[1]-(self.config['Food']['size']/2), f[0]+(self.config['Food']['size']/2), f[1]+(self.config['Food']['size']/2), fill="#FF0000", outline="#FFFFFF")
            for x, y in self.trail:
                self.canvas.create_line(x, y, x+1, y+1, fill="red")
            possible_babies = agent.evolve_if_possible()
            if possible_babies:
                new_agents+=possible_babies
        
        #remove dead agents
        while len(dead_agents) > 0:
            self.agents = self.agents[:dead_agents[0]] + self.agents[dead_agents[0]+1:]
            dead_agents = dead_agents[1:]
        
        #evolved children
        self.agents += new_agents
        
        # Standard 60 FPS refresh rate target (~16ms)
        self.root.after(16, self.run_loop)