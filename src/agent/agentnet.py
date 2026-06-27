import torch
import torch.nn as nn
import torch.optim as optim

class AgentNetwork(nn.Module):
    def __init__(self, input_length=5, output_length=2):
        super(AgentNetwork, self).__init__()
        self.fc1 = nn.Linear(input_length, output_length)
        # self.fc2 = nn.Linear(10, output_length)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        x = self.fc1(x)
        # x = self.relu(x)
        # x = self.fc2(x)
        x[:,0] = 2 * (self.sigmoid(x[:,0]) - 0.5)
        x[:,1] = self.relu(x[:,1]) + 1.0
        return x