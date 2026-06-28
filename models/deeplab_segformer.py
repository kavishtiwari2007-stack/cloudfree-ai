import torch
import torch.nn as nn
import torch.nn.functional as F

# ==========================================
# 1. DEEPLABV3+ FLOOD SEGMENTATION MODEL
# ==========================================

class ASPPConv(nn.Sequential):
    def __init__(self, in_channels, out_channels, dilation):
        super().__init__(
            nn.Conv2d(in_channels, out_channels, 3, padding=dilation, dilation=dilation, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

class ASPPPooling(nn.Sequential):
    def __init__(self, in_channels, out_channels):
        super().__init__(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(in_channels, out_channels, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        size = x.shape[-2:]
        for mod in self:
            x = mod(x)
        return F.interpolate(x, size=size, mode='bilinear', align_corners=True)

class ASPP(nn.Module):
    """Atrous Spatial Pyramid Pooling module for multi-scale receptive fields"""
    def __init__(self, in_channels, atrous_rates, out_channels=256):
        super().__init__()
        modules = [
            nn.Sequential(nn.Conv2d(in_channels, out_channels, 1, bias=False), nn.BatchNorm2d(out_channels), nn.ReLU(inplace=True)),
            ASPPConv(in_channels, out_channels, atrous_rates[0]),
            ASPPConv(in_channels, out_channels, atrous_rates[1]),
            ASPPConv(in_channels, out_channels, atrous_rates[2]),
            ASPPPooling(in_channels, out_channels)
        ]
        self.convs = nn.ModuleList(modules)
        self.project = nn.Sequential(
            nn.Conv2d(len(modules) * out_channels, out_channels, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5)
        )

    def forward(self, x):
        res = [conv(x) for conv in self.convs]
        res = torch.cat(res, dim=1)
        return self.project(res)


class DeepLabV3Plus(nn.Module):
    """
    DeepLabV3+ architecture with custom remote sensing configuration.
    Inputs: 4 Channels (Reconstructed RGB + NIR).
    Outputs: Binary Segmentation (2 classes: Flood Water, Background).
    """
    def __init__(self, in_channels=4, num_classes=2):
        super().__init__()
        # Backbone (Simple simulated ResNet encoder)
        self.backbone_low = nn.Sequential(
            nn.Conv2d(in_channels, 64, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True)
        )
        self.backbone_high = nn.Sequential(
            nn.MaxPool2d(2), # 1/2
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1, bias=False), # 1/4
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 512, kernel_size=3, stride=2, padding=1, bias=False), # 1/8
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True)
        )

        # ASPP Module
        self.aspp = ASPP(512, atrous_rates=[6, 12, 18], out_channels=256)
        
        # Low-level feature projection
        self.project_low = nn.Sequential(
            nn.Conv2d(64, 48, 1, bias=False),
            nn.BatchNorm2d(48),
            nn.ReLU(inplace=True)
        )
        
        # Final classifier head
        self.classifier = nn.Sequential(
            nn.Conv2d(256 + 48, 256, 3, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, num_classes, 1)
        )

    def forward(self, x):
        # x: [B, 4, H, W]
        input_size = x.shape[-2:]
        
        low_level_feat = self.backbone_low(x)
        high_level_feat = self.backbone_high(low_level_feat)
        
        # ASPP on deep features
        aspp_out = self.aspp(high_level_feat)
        aspp_out = F.interpolate(aspp_out, size=low_level_feat.shape[-2:], mode='bilinear', align_corners=True)
        
        # Merge with projected low-level features
        proj_low = self.project_low(low_level_feat)
        merged = torch.cat([aspp_out, proj_low], dim=1)
        
        logits = self.classifier(merged)
        # Upsample to match original image size
        return F.interpolate(logits, size=input_size, mode='bilinear', align_corners=True)


# ==========================================
# 2. SEGFORMER FLOOD SEGMENTATION ARCHITECTURE
# ==========================================

class MLPBlock(nn.Module):
    """Linear projection layer for SegFormer's All-MLP Decoder"""
    def __init__(self, in_dim, out_dim=256):
        super().__init__()
        self.proj = nn.Linear(in_dim, out_dim)

    def forward(self, x):
        # x: [B, C, H, W]
        B, C, H, W = x.shape
        x_flat = x.flatten(2).transpose(1, 2) # [B, H*W, C]
        proj_out = self.proj(x_flat) # [B, H*W, out_dim]
        return proj_out.transpose(1, 2).view(B, -1, H, W)


class SegFormerFloodNet(nn.Module):
    """
    SegFormer model customized for remote sensing flood mapping.
    Uses multi-stage hierarchical MLP projections.
    """
    def __init__(self, in_channels=4, num_classes=2, embed_dims=[32, 64, 128, 256]):
        super().__init__()
        # Hierarchical Patch Encoders (Simulating Vision Transformer Stages)
        self.stage1 = nn.Sequential(
            nn.Conv2d(in_channels, embed_dims[0], kernel_size=7, stride=4, padding=3),
            nn.BatchNorm2d(embed_dims[0]),
            nn.ReLU(inplace=True)
        )
        self.stage2 = nn.Sequential(
            nn.Conv2d(embed_dims[0], embed_dims[1], kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(embed_dims[1]),
            nn.ReLU(inplace=True)
        )
        self.stage3 = nn.Sequential(
            nn.Conv2d(embed_dims[1], embed_dims[2], kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(embed_dims[2]),
            nn.ReLU(inplace=True)
        )
        self.stage4 = nn.Sequential(
            nn.Conv2d(embed_dims[2], embed_dims[3], kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(embed_dims[3]),
            nn.ReLU(inplace=True)
        )

        # All-MLP Decoder Head
        self.mlp1 = MLPBlock(embed_dims[0], 128)
        self.mlp2 = MLPBlock(embed_dims[1], 128)
        self.mlp3 = MLPBlock(embed_dims[2], 128)
        self.mlp4 = MLPBlock(embed_dims[3], 128)
        
        self.linear_fuse = nn.Sequential(
            nn.Conv2d(128 * 4, 256, kernel_size=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True)
        )
        
        self.classifier = nn.Conv2d(256, num_classes, kernel_size=1)

    def forward(self, x):
        # x shape: [B, 4, H, W]
        input_size = x.shape[-2:]
        
        # Encoders
        s1 = self.stage1(x) # 1/4
        s2 = self.stage2(s1) # 1/8
        s3 = self.stage3(s2) # 1/16
        s4 = self.stage4(s3) # 1/32

        # Decoder MLPs
        d1 = self.mlp1(s1)
        d2 = self.mlp2(s2)
        d3 = self.mlp3(s3)
        d4 = self.mlp4(s4)

        # Resize all features to stage1 dimensions (1/4)
        target_size = s1.shape[-2:]
        d2_up = F.interpolate(d2, size=target_size, mode='bilinear', align_corners=True)
        d3_up = F.interpolate(d3, size=target_size, mode='bilinear', align_corners=True)
        d4_up = F.interpolate(d4, size=target_size, mode='bilinear', align_corners=True)
        
        # Concatenate & Predict
        fused = torch.cat([d1, d2_up, d3_up, d4_up], dim=1)
        feat = self.linear_fuse(fused)
        logits = self.classifier(feat)
        
        # Final upsample to match original input size
        return F.interpolate(logits, size=input_size, mode='bilinear', align_corners=True)
