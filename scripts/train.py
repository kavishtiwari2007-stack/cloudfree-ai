import os
import sys
import argparse
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import numpy as np

# Add project root to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.unet_cloudnet import UNet, DiceBCELoss
from models.temporal_transformer import TemporalFusionTransformer
from models.pix2pix_diffusion import DSen2CRReconstructor
from models.deeplab_segformer import DeepLabV3Plus
from models.siamese_transformer import SiameseViTChangeDetector

class MockSatelliteDataset(Dataset):
    """Generates synthetic tensor structures mapping LISS-IV & SAR telemetry shapes for pipeline testing"""
    def __init__(self, length=32):
        self.length = length

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        # Outputs: historical (4 bands), current cloudy (4 bands), current SAR (2 bands), target clear (4 bands)
        return {
            "historical": torch.rand(4, 256, 256),
            "cloudy": torch.rand(4, 256, 256),
            "sar": torch.rand(2, 256, 256),
            "target": torch.rand(4, 256, 256),
            "cloud_mask": torch.randint(0, 3, (256, 256)).long()
        }

def train_model(model_name: str, epochs: int, batch_size: int, lr: float, save_dir: str):
    print(f"Initializing training pipeline for model: {model_name}")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Execution Target Device: {device}")

    # Instantiate datasets
    dataset = MockSatelliteDataset()
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Model selector
    if model_name == "unet":
        model = UNet(n_channels=4, n_classes=3).to(device)
        criterion = DiceBCELoss()
    elif model_name == "fusion":
        model = TemporalFusionTransformer().to(device)
        criterion = nn.MSELoss()
    elif model_name == "reconstruction":
        model = DSen2CRReconstructor().to(device)
        criterion = nn.L1Loss()
    elif model_name == "flood":
        model = DeepLabV3Plus(in_channels=4, num_classes=2).to(device)
        criterion = nn.CrossEntropyLoss()
    else:
        raise ValueError(f"Unrecognized model type: {model_name}")

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    
    os.makedirs(save_dir, exist_ok=True)
    print("Beginning Training Loop...")

    for epoch in range(1, epochs + 1):
        model.train()
        epoch_loss = 0.0
        
        for batch_idx, batch in enumerate(loader):
            optimizer.zero_grad()
            
            if model_name == "unet":
                inputs = batch["cloudy"].to(device)
                targets = batch["cloud_mask"].to(device)
                outputs = model(inputs)
                loss = criterion(outputs, targets)
            elif model_name == "fusion":
                hist = batch["historical"].to(device)
                sar = batch["sar"].to(device)
                outputs = model(hist, sar)
                loss = criterion(outputs, torch.rand_like(outputs)) # Mock loss
            elif model_name == "reconstruction":
                # Fused features mock
                fused = torch.rand(batch_size, 128, 64, 64).to(device)
                targets = batch["target"].to(device)
                # Resize targets to match spatial size of bottleneck if needed
                targets_resized = torch.nn.functional.interpolate(targets, size=(64, 64))
                outputs = model(fused)
                loss = criterion(outputs, targets_resized)
            elif model_name == "flood":
                inputs = batch["target"].to(device)
                targets = torch.randint(0, 2, (batch_size, 256, 256)).to(device)
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            
        mean_loss = epoch_loss / len(loader)
        print(f"Epoch [{epoch}/{epochs}] | Mean Batch Loss: {mean_loss:.4f}")
        
        # Save checkpointer
        if epoch % 5 == 0 or epoch == epochs:
            chk_path = os.path.join(save_dir, f"{model_name}_epoch_{epoch}.pth")
            torch.save(model.state_dict(), chk_path)
            print(f"Checkpoint saved: {chk_path}")

    print("Training finished successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CloudFreeAI Training CLI")
    parser.add_argument("--model", type=str, default="unet", choices=["unet", "fusion", "reconstruction", "flood"])
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--save-dir", type=str, default="./checkpoints")
    args = parser.parse_args()
    
    train_model(args.model, args.epochs, args.batch_size, args.lr, args.save_dir)
