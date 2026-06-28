import torch
import torch.nn as nn
import torch.nn.functional as F

class ResEncoderBlock(nn.Module):
    """Residual convolution block to extract features in Siamese channels"""
    def __init__(self, in_c, out_c, stride=1):
        super().__init__()
        self.conv1 = nn.Conv2d(in_c, out_c, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_c)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_c, out_c, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_c)
        
        self.shortcut = nn.Sequential()
        if stride != 1 or in_c != out_c:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_c, out_c, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_c)
            )

    def forward(self, x):
        residual = self.shortcut(x)
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += residual
        return self.relu(out)


class SiameseFeatureExtractor(nn.Module):
    """Extracts features in twin networks (shared weights)"""
    def __init__(self, in_channels=4, feat_dim=128):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(in_channels, 64, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            ResEncoderBlock(64, 64),
            ResEncoderBlock(64, 128, stride=2), # Down 1/2
            ResEncoderBlock(128, feat_dim, stride=2) # Down 1/4
        )

    def forward(self, x):
        return self.encoder(x)


class SiameseViTChangeDetector(nn.Module):
    """
    Siamese Vision Transformer for disaster change detection.
    Inputs:
      - historical_opt: [B, 4, H, W] (Pre-disaster optical)
      - reconstructed_opt: [B, 4, H, W] (Post-disaster cloud-free optical)
    Outputs:
      - change_logits: [B, 1, H, W] (Pixel-level change map)
      - classification_logits: [B, 4, H, W] (Low-level classification of change type:
        0=No Change, 1=Inundated Settlement, 2=Vegetation Loss, 3=Road/Infrastructure Break)
    """
    def __init__(self, in_channels=4, feat_dim=128, nhead=4, num_classes=4):
        super().__init__()
        # Shared weight Siamese encoder
        self.feature_extractor = SiameseFeatureExtractor(in_channels, feat_dim)
        
        # Self-Attention transformer encoder to capture spatial relations
        encoder_layer = nn.TransformerEncoderLayer(d_model=feat_dim, nhead=nhead, dim_feedforward=feat_dim*2, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=2)
        
        # Classifier heads
        self.up = nn.Upsample(scale_factor=4, mode='bilinear', align_corners=True)
        self.change_head = nn.Conv2d(feat_dim, 1, kernel_size=3, padding=1)
        self.class_head = nn.Conv2d(feat_dim, num_classes, kernel_size=3, padding=1)

    def forward(self, historical_opt, reconstructed_opt):
        # 1. Feed into shared weight feature extractor
        h_feat = self.feature_extractor(historical_opt)
        r_feat = self.feature_extractor(reconstructed_opt)
        
        # 2. Extract differences
        diff_feat = torch.abs(r_feat - h_feat) # [B, feat_dim, H/4, W/4]
        B, D, H_down, W_down = diff_feat.shape
        
        # 3. Spatial attention encoding
        # Flatten spatial dimensions: [B, H_down*W_down, D]
        flat_diff = diff_feat.view(B, D, H_down * W_down).permute(0, 2, 1)
        trans_out = self.transformer(flat_diff)
        
        # Reshape to image dimensions
        spatial_feats = trans_out.permute(0, 2, 1).view(B, D, H_down, W_down)
        
        # 4. Upsample and predict
        spatial_feats_up = self.up(spatial_feats) # Match input resolution H, W
        
        change_logits = self.change_head(spatial_feats_up)
        class_logits = self.class_head(spatial_feats_up)
        
        return change_logits, class_logits
