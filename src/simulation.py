import tkinter as tk
import math
from src.agent.agent import Agent
import random

class Simulation:
    def __init__(self, root, agent_size:int, screen_width:int, screen_height:int, eat_amount:int=200, food_size:int=8, num_agents:int=8, num_food:int=50):
        self.root = root
        self.root.title("2D Agent Food Simulation")

        # Set constants
        self.num_agents = num_agents
        self.num_food = num_food
        self.food_size = food_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.agent_size = agent_size
        self.eat_amount = eat_amount
        self.trail = []
        # Setup Canvas
        self.canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg="#222222")
        self.canvas.pack()

        # Initialize entities
        self.agents = [Agent(ray_count=50, food=300, food_size=self.food_size, screen_width=self.screen_width, screen_height=self.screen_height, size=self.agent_size) for _ in range(self.num_agents)]
        self.foods = [[random.uniform(20, self.screen_width-20), random.uniform(20, self.screen_height-20)] for _ in range(self.num_food)]
        
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
                fx - self.food_size/2, fy - self.food_size/2,
                fx + self.food_size/2, fy + self.food_size/2,
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
                if math.hypot(agent.x - food[0], agent.y - food[1]) < (self.agent_size + self.food_size) / 2:
                    # Eat food and respawn it elsewhere
                    self.foods[i] = [random.uniform(20, self.screen_width-20), random.uniform(20, self.screen_height-20)]
                    agent.food += self.eat_amount
            # Draw oriented triangle geometry
            coords = agent.get_triangle_coords()
            self.canvas.create_polygon(coords, fill="#00BCD4", outline="#FFFFFF")
            
            for f in agent.highlights:
                self.canvas.create_rectangle(f[0]-(self.food_size/2), f[1]-(self.food_size/2), f[0]+(self.food_size/2), f[1]+(self.food_size/2), fill="#FF0000", outline="#FFFFFF")
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