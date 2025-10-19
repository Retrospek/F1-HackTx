import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

import numpy as np
import pandas as pd

class TyreDegDataset(Dataset):
    def __init__(self, data, seq_len=10, target_col="lap_time"):
        self.seq_len = seq_len
        self.target = target_col

        self.groups = []

        for driver, grp in data.groupby('driver'):
            lapNum = grp.sort_values("lap_number")
            ftres = grp.drop(columns=["timestamp", "driver", "flag_status", "push_signal",
                          "tyre_compound", "drs_status", "weather_condition", target_col])
            ftres = ftres.apply(pd.to_numeric, errors='coerce').fillna(0).values  # force numeric, fill NaN

            trgts = grp[target_col].values

            for i in range(len(grp) - seq_len):
                self.groups.append((ftres[i:i+seq_len], trgts[i+seq_len]))
    
    def __len__(self):
        return len(self.groups)
    
    def __getitem__(self, idx):
        features_seq, target = self.groups[idx]
        features_seq = torch.tensor(features_seq, dtype=torch.float32)
        target = torch.tensor(target, dtype=torch.float32)
        
        return features_seq, target

class MDNNetwork(nn.Module):
    def __init__(self, in_dim=140, action_dim=3, latent_dim=64, out_dim=1):
        """
        Args:
            in_dim: Number of input features (after LSTM or raw)
            hidden_dim: Hidden layer size
            num_gaussians: Number of mixture components K
            out_dim: Dimension of the target (e.g., 1 for lap_time)
        """
        super().__init__()
        self.K = action_dim # Otherwise known as the number of possible actions to be taken
                                            # K or the num_gaussians represents the num of modes
        self.out_dim = out_dim

        self.net = nn.Sequential(
            nn.Linear(in_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, latent_dim),
        )

        # Each Gaussian needs mu, sigma, and a mixture weight (pi)
        self.fc_mu = nn.Linear(latent_dim, action_dim * out_dim)
        self.fc_sigma = nn.Linear(latent_dim, action_dim * out_dim)
        self.fc_sigma.bias.data.fill_(0.0)  # so exp(0)=1 as starting sigma

        self.fc_pi = nn.Linear(latent_dim, self.K)

    def forward(self, x):
        h = self.net(x)

        mu = self.fc_mu(h)                         # shape: [B, K*out_dim]
        sigma = F.softplus(self.fc_sigma(h)) + 1e-3

        pi = F.softmax(self.fc_pi(h), dim=1)       # mixture weights sum to 1

        mu = mu.view(-1, self.K, self.out_dim)
        sigma = sigma.view(-1, self.K, self.out_dim)
        
        return mu, sigma, pi
    
def mdn_loss(y, mu, sigma, pi, eps=1e-8):
    if y.dim() == 1:
        y = y.unsqueeze(-1)

    # Expand y to match [B, K, out_dim]
    y_expanded = y.unsqueeze(1)  
    y_expanded = y_expanded.expand_as(mu)  

    # Gaussian log like...
    log_prob = -0.5 * ((y_expanded - mu) / sigma) ** 2 - torch.log(sigma) - 0.5 * np.log(2*np.pi)
    
    # Sum over out_dim
    log_prob = log_prob.sum(dim=2)

    # Add log mixture weights
    log_weighted = log_prob + torch.log(pi + eps)

    # Log-sum-exp trick for stability
    max_log = torch.max(log_weighted, dim=1, keepdim=True)[0]  # [B,1]
    log_sum = max_log + torch.log(torch.sum(torch.exp(log_weighted - max_log), dim=1, keepdim=True))  # [B,1]

    nll = -log_sum.mean()
    return nll
