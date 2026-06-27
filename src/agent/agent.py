import math
import random
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
import tqdm
import numpy as np
from src.agent.agentnet import AgentNetwork
import torch.optim.lr_scheduler as lr_scheduler

class Agent:
    def __init__(self, config: dict):
        self.config = config
        self.speed = 1
        self.x = random.uniform(50, config['Simulation']['screen_width'] - 50)
        self.y = random.uniform(50, config['Simulation']['screen_height'] - 50)
        self.angle = random.uniform(0, 2 * math.pi)
        self.food = self.config['Agent']['starting_food']
        self.net = AgentNetwork(self.config['Agent']['ray_count'], 2)
        self.highlights = []

    def _ray(self, angle, foods):
        min_dist = self.config['Agent']['max_ray_dist']
        ray_vec = np.array([np.cos(angle), np.sin(angle)])
        closest_food = None
        for f in foods:
            fx, fy = f[0], f[1]

            #normalized vector to get to the food
            to_obj_vec = np.array([fx - self.x, fy - self.y])
            to_obj_vec = to_obj_vec / np.linalg.norm(to_obj_vec)

            #is it a close enough angle?
            cos_sim = to_obj_vec @ ray_vec
            angle = np.arccos(cos_sim)
            
            dist_to_me = ((fx - self.x) ** 2 + (fy - self.y) ** 2)
            if np.abs(angle) < (2 / self.config['Agent']['ray_count']) and dist_to_me < min_dist:
                min_dist = dist_to_me
                closest_food = f
        if closest_food is not None:
            self.highlights.append(closest_food)
        return min_dist
    
    def _input_to_model(self, foods):
        self.highlights = []
        ray_angles = np.linspace(-1,1,self.config['Agent']['ray_count']) + self.angle
        ray_angles[ray_angles > 2 * np.pi] -= 2 * np.pi
        ray_angles[ray_angles < 0] += 2 * np.pi
        dists_to_food = torch.tensor([self._ray(ray_angle, foods) for ray_angle in ray_angles])
        dists_to_food = 1 - (dists_to_food /  self.config['Agent']['max_ray_dist'])
        return dists_to_food

    def update(self, foods):
        dists_to_food = self._input_to_model(foods)

        self.net.eval()
        with torch.no_grad():
            output = self.net(dists_to_food[None])
            angle_delta, new_speed = output[0]
        self.angle += angle_delta.item()
        self.speed = new_speed.item()

        # Move toward food
        vx = math.cos(self.angle) * self.speed
        vy = math.sin(self.angle) * self.speed
        self.food -= np.sqrt(self.speed/2)
        self.x += vx
        self.y += vy

    def get_triangle_coords(self):
        # Point 1: Tip of the triangle (facing forward)
        pt1_x = self.x + self.config['Agent']['size'] * math.cos(self.angle)
        pt1_y = self.y + self.config['Agent']['size'] * math.sin(self.angle)
        
        # Point 2: Rear left flank
        pt2_x = self.x + (self.config['Agent']['size'] / 2) * math.cos(self.angle + 2.5)
        pt2_y = self.y + (self.config['Agent']['size'] / 2) * math.sin(self.angle + 2.5)
        
        # Point 3: Rear right flank
        pt3_x = self.x + (self.config['Agent']['size'] / 2) * math.cos(self.angle - 2.5)
        pt3_y = self.y + (self.config['Agent']['size'] / 2) * math.sin(self.angle - 2.5)
        
        return [pt1_x, pt1_y, pt2_x, pt2_y, pt3_x, pt3_y]

    def pretrain(self):
        self.net.train()
        criterion = nn.MSELoss()
        optimizer = optim.AdamW(self.net.parameters(), lr=5e-3)
        scheduler = lr_scheduler.CosineAnnealingLR(optimizer, T_max=100, eta_min=1e-5)

        num_epochs = 100
        losses_over_time = []
        for epoch in (pbar := tqdm.trange(num_epochs)):
            input = None
            target = None
            optimizer.zero_grad(set_to_none=True)
            for _ in range(100):
                angle = random.uniform(-1, 1)
                dist = random.uniform(0, 100)
                fx, fy = self.x + (math.cos(self.angle + angle) * dist), self.y + (math.sin(self.angle + angle) * dist)
                inputs = [[fx, fy]]

                #generate ones farther away
                for _ in range(random.randint(0,5)):
                    farther_angle = random.uniform(-1, 1)
                    farther_dist = random.uniform(dist+1, self.config['Agent']['max_ray_dist'] / 5)
                    fx, fy = self.x + (math.cos(self.angle + farther_angle) * farther_dist), self.y + (math.sin(self.angle + farther_angle) * farther_dist)
                    inputs.append([fx, fy])
                
                this_input = torch.Tensor(self._input_to_model(inputs))[None,:]
                this_target = torch.Tensor([angle])[None,:]
                if input is None:
                    input  = this_input
                    target = this_target
                else:
                    input = torch.concatenate((this_input,   input),  dim=0)
                    target = torch.concatenate((this_target, target), dim=0)
            outputs = self.net(input)        
            loss = criterion(outputs[:,0], target)  
            pbar.set_description(str(loss.item()))
            losses_over_time.append(loss.item())   
            loss.backward()                       
            optimizer.step()
            scheduler.step()

    def is_dead(self):
        return self.food <= 0 or self.x < 0 or self.x > self.config['Simulation']['screen_width'] or self.y < 0 or self.y > self.config['Simulation']['screen_width']

    def copy(self):
        baby = Agent(config=self.config)
        baby.food = 120
        baby.net.load_state_dict(self.net.state_dict())
        return baby

    def _perform_evolve(self):
        babies = []
        for _ in range(2):
            with torch.no_grad():
                baby = self.copy()
                for _, param in baby.net.named_parameters():
                    param += torch.randn(param.shape) * 1e-3
            babies.append(baby)
        self.food -= 60
        return babies

    def evolve_if_possible(self):
        if self.food > 300:
            return self._perform_evolve()
        return None
