import torch
import torch.nn as nn
import torch.nn.functional as F

# ==========================================
# 1. PIX2PIX / CONDITIONAL GAN ARCHITECTURE
# ==========================================

class PatchGANDiscriminator(nn.Module):
    """
    PatchGAN Discriminator for Pix2Pix.
    Classifies patch regions (e.g. 70x70) as real or fake to preserve sharp textures.
    """
    def __init__(self, in_channels=8): # 4 channels conditional target + 4 channels test image
        super().__init__()
        
        def filter_block(in_c, out_c, normalize=True):
            layers = [nn.Conv2d(in_c, out_c, kernel_size=4, stride=2, padding=1)]
            if normalize:
                layers.append(nn.InstanceNorm2d(out_c))
            layers.append(nn.LeakyReLU(0.2, inplace=True))
            return nn.Sequential(*layers)

        self.model = nn.Sequential(
            filter_block(in_channels, 64, normalize=False),
            filter_block(64, 128),
            filter_block(128, 256),
            filter_block(256, 512),
            nn.ZeroPad2d((1, 0, 1, 0)),
            nn.Conv2d(512, 1, kernel_size=4, padding=1) # Logits map
        )

    def forward(self, opt_cond, opt_target):
        # Concatenate optical conditions and target images along the channel dim
        x = torch.cat([opt_cond, opt_target], dim=1)
        return self.model(x)


# ==========================================
# 2. DSEN2-CR RESIDUAL RECONSTRUCTION MODEL
# ==========================================

class DSen2CRBlock(nn.Module):
    """Deep Residual Block for cloud removal"""
    def __init__(self, channels):
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x):
        return x + self.bn2(self.conv2(self.relu(self.bn1(self.conv1(x)))))


class DSen2CRReconstructor(nn.Module):
    """
    DSen2-CR inspired Deep Residual Network.
    Accepts fused embeddings and maps them directly to high-res optical channels.
    """
    def __init__(self, in_channels=128, out_channels=4, num_blocks=8):
        super().__init__()
        self.init_conv = nn.Conv2d(in_channels, 128, kernel_size=3, padding=1)
        
        self.res_blocks = nn.Sequential(
            *[DSen2CRBlock(128) for _ in range(num_blocks)]
        )
        
        self.out_conv = nn.Sequential(
            nn.Conv2d(128, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, out_channels, kernel_size=3, padding=1),
            nn.Sigmoid() # Normalize pixel outputs [0, 1]
        )

    def forward(self, fused_features):
        x = self.init_conv(fused_features)
        x = self.res_blocks(x)
        return self.out_conv(x)


# ==========================================
# 3. CONDITIONAL DIFFUSION U-NET BOTTLENECK
# ==========================================

class TimeEmbedding(nn.Module):
    """Maps timestep scalar t to sinusoidal embeddings"""
    def __init__(self, dim):
        super().__init__()
        self.dim = dim

    def forward(self, t):
        # t is shape [B]
        device = t.device
        half_dim = self.dim // 2
        embeddings = torch.log(torch.tensor(10000.0, device=device)) / (half_dim - 1)
        embeddings = torch.exp(torch.arange(half_dim, device=device) * -embeddings)
        embeddings = t[:, None] * embeddings[None, :]
        embeddings = torch.cat((embeddings.sin(), embeddings.cos()), dim=-1)
        return embeddings


class ConditionalUNetDiffusion(nn.Module):
    """
    Conditional U-Net denoising network for Diffusion pixel reconstruction.
    Conditioned on spatial-temporal fused embeddings [B, 128, H, W].
    Denoises inputs of size [B, 4, H, W] (Noisy optical image).
    """
    def __init__(self, cond_dim=128, opt_channels=4, time_dim=64):
        super().__init__()
        self.time_mlp = nn.Sequential(
            TimeEmbedding(time_dim),
            nn.Linear(time_dim, time_dim),
            nn.ReLU(inplace=True)
        )
        
        # Encoder Projectors
        self.proj_in = nn.Conv2d(opt_channels, 64, kernel_size=3, padding=1)
        self.proj_cond = nn.Conv2d(cond_dim, 64, kernel_size=3, padding=1)
        
        # Combined Conv stages
        self.conv1 = nn.Conv2d(128 + time_dim, 128, kernel_size=3, padding=1)
        self.res1 = DSen2CRBlock(128)
        self.conv2 = nn.Conv2d(128, 64, kernel_size=3, padding=1)
        self.proj_out = nn.Conv2d(64, opt_channels, kernel_size=3, padding=1)

    def forward(self, x_noisy, t_step, fused_cond):
        # x_noisy: [B, 4, H, W]
        # t_step: [B]
        # fused_cond: [B, 128, H, W]
        B, _, H, W = x_noisy.shape
        
        # Embed time
        t_emb = self.time_mlp(t_step) # [B, time_dim]
        t_emb_spatial = t_emb.view(B, -1, 1, 1).expand(-1, -1, H, W)
        
        # Project inputs
        x_proj = self.proj_in(x_noisy)
        c_proj = self.proj_cond(fused_cond)
        
        # Concatenate noisy image, conditional embedding, and temporal step
        combined = torch.cat([x_proj, c_proj, t_emb_spatial], dim=1) # [B, 64 + 64 + time_dim, H, W]
        
        feat = F.relu(self.conv1(combined))
        feat = self.res1(feat)
        feat = F.relu(self.conv2(feat))
        
        # Predict noise profile
        predicted_noise = self.proj_out(feat)
        return predicted_noise
