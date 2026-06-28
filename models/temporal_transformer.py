import torch
import torch.nn as nn
import torch.nn.functional as F

class ResBlock(nn.Module):
    """Residual convolution block to preserve spatial gradients"""
    def __init__(self, channels):
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x):
        residual = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        out += residual
        return self.relu(out)

class SensorEncoder(nn.Module):
    """Feature projection encoder for satellite bands"""
    def __init__(self, in_channels, latent_dim=128):
        super().__init__()
        self.init_conv = nn.Sequential(
            nn.Conv2d(in_channels, 64, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True)
        )
        self.res_blocks = nn.Sequential(
            ResBlock(64),
            ResBlock(64)
        )
        self.proj_conv = nn.Conv2d(64, latent_dim, kernel_size=1)

    def forward(self, x):
        x = self.init_conv(x)
        x = self.res_blocks(x)
        return self.proj_conv(x)

class CrossAttentionModule(nn.Module):
    """
    Cross-Attention layer fusing SAR and Optical features.
    SAR guides the attention weights over historical Optical features.
    """
    def __init__(self, d_model, nhead=4):
        super().__init__()
        self.mha = nn.MultiheadAttention(embed_dim=d_model, num_heads=nhead, batch_first=True)
        self.norm = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_model * 2),
            nn.ReLU(inplace=True),
            nn.Linear(d_model * 2, d_model)
        )
        self.norm2 = nn.LayerNorm(d_model)

    def forward(self, opt_feat, sar_feat):
        # inputs shape: [B, D, H, W]
        B, D, H, W = opt_feat.shape
        
        # Flatten spatial dimensions for Transformer attention: [B, H*W, D]
        opt_flat = opt_feat.view(B, D, H * W).permute(0, 2, 1)
        sar_flat = sar_feat.view(B, D, H * W).permute(0, 2, 1)
        
        # Cross Attention query=sar, key/value=optical
        attn_out, _ = self.mha(query=sar_flat, key=opt_flat, value=opt_flat)
        x = self.norm(sar_flat + attn_out)
        
        # Feedforward
        ffn_out = self.ffn(x)
        x = self.norm2(x + ffn_out)
        
        # Reshape back to image dimensions: [B, D, H, W]
        return x.permute(0, 2, 1).view(B, D, H, W)


class TemporalFusionTransformer(nn.Module):
    """
    Main Spatial-Temporal Fusion network.
    Combines Historical LISS-IV (RGB+NIR) and Current SAR (VV+VH)
    to output fused feature maps.
    """
    def __init__(self, opt_channels=4, sar_channels=2, latent_dim=128, n_heads=4):
        super().__init__()
        # 1. Specialized sensor encoders
        self.optical_encoder = SensorEncoder(opt_channels, latent_dim)
        self.sar_encoder = SensorEncoder(sar_channels, latent_dim)
        
        # 2. Cross-Attention block
        self.cross_attn = CrossAttentionModule(latent_dim, n_heads)
        
        # 3. Post-fusion refinement
        self.refine = nn.Sequential(
            ResBlock(latent_dim),
            nn.Conv2d(latent_dim, latent_dim, kernel_size=3, padding=1),
            nn.BatchNorm2d(latent_dim),
            nn.ReLU(inplace=True)
        )

    def forward(self, historical_opt, current_sar):
        # 1. Project into same embedding space
        opt_emb = self.optical_encoder(historical_opt)
        sar_emb = self.sar_encoder(current_sar)
        
        # 2. Inter-sensor cross-attention
        fused_emb = self.cross_attn(opt_emb, sar_emb)
        
        # 3. Spatial refinement
        output = self.refine(fused_emb)
        return output
