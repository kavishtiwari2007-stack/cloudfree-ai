import torch
import torch.nn as nn
import torch.nn.functional as F

class DoubleConv(nn.Module):
    """(convolution => [BN] => ReLU) * 2"""
    def __init__(self, in_channels, out_channels, mid_channels=None):
        super().__init__()
        if not mid_channels:
            mid_channels = out_channels
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, mid_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(mid_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(mid_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.double_conv(x)

class Down(nn.Module):
    """Downscaling with maxpool then double conv"""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.maxpool_conv = nn.Sequential(
            nn.MaxPool2d(2),
            DoubleConv(in_channels, out_channels)
        )

    def forward(self, x):
        return self.maxpool_conv(x)

class Up(nn.Module):
    """Upscaling then double conv"""
    def __init__(self, in_channels, out_channels, bilinear=True):
        super().__init__()

        # if bilinear, use the normal convolutions to reduce the number of channels
        if bilinear:
            self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
            self.conv = DoubleConv(in_channels, out_channels, in_channels // 2)
        else:
            self.up = nn.ConvTranspose2d(in_channels, in_channels // 2, kernel_size=2, stride=2)
            self.conv = DoubleConv(in_channels, out_channels)

    def forward(self, x1, x2):
        x1 = self.up(x1)
        # input is CHW
        diffY = x2.size()[2] - x1.size()[2]
        diffX = x2.size()[3] - x1.size()[3]

        x1 = F.pad(x1, [diffX // 2, diffX - diffX // 2,
                        diffY // 2, diffY - diffY // 2])
        # Concatenate along the channel dimension
        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)

class OutConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(OutConv, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)

    def forward(self, x):
        return self.conv(x)


class UNet(nn.Module):
    """
    Standard U-Net Architecture for Remote Sensing Image Segmentation.
    Optimized for multi-spectral band alignment (4 input channels: R, G, B, NIR).
    """
    def __init__(self, n_channels=4, n_classes=3, bilinear=False):
        super(UNet, self).__init__()
        self.n_channels = n_channels
        self.n_classes = n_classes
        self.bilinear = bilinear

        self.inc = DoubleConv(n_channels, 64)
        self.down1 = Down(64, 128)
        self.down2 = Down(128, 256)
        self.down3 = Down(256, 512)
        factor = 2 if bilinear else 1
        self.down4 = Down(512, 1024 // factor)
        
        self.up1 = Up(1024, 512 // factor, bilinear)
        self.up2 = Up(512, 256 // factor, bilinear)
        self.up3 = Up(256, 128 // factor, bilinear)
        self.up4 = Up(128, 64, bilinear)
        self.outc = OutConv(64, n_classes)

    def forward(self, x):
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)
        x = self.up1(x5, x4)
        x = self.up2(x, x3)
        x = self.up3(x, x2)
        x = self.up4(x, x1)
        logits = self.outc(x)
        return logits


class DilatedConvBlock(nn.Module):
    """Dilated Convolutions to expand receptive field without losing resolution"""
    def __init__(self, in_ch, out_ch, dilation_rate):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=dilation_rate, dilation=dilation_rate, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.conv(x)


class CloudNet(nn.Module):
    """
    Cloud-Net: Dilated multi-scale skip connection network for high-res satellite cloud detection.
    Inputs: 4 Channels (RGB + NIR)
    Outputs: 3 Classes (Clear, Cloud, Cloud Shadow)
    """
    def __init__(self, in_channels=4, out_classes=3):
        super(CloudNet, self).__init__()
        # Encoder
        self.conv1 = DoubleConv(in_channels, 64)
        self.down1 = nn.MaxPool2d(2)
        
        self.conv2 = DoubleConv(64, 128)
        self.down2 = nn.MaxPool2d(2)
        
        # Dilated Bottleneck (Multi-Scale Context)
        self.dilated1 = DilatedConvBlock(128, 256, dilation_rate=2)
        self.dilated2 = DilatedConvBlock(256, 256, dilation_rate=4)
        self.dilated3 = DilatedConvBlock(256, 128, dilation_rate=2)

        # Decoder
        self.up1 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.dec_conv1 = DoubleConv(128, 64) // Skip connection from conv2 (64 + 64) -> actually conv2 is 128 ch!
        # Correct dimensions for decoders
        self.up_trans1 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.dec1 = DoubleConv(128, 64) # concat up_trans1 (64) + conv1 (64)
        
        self.out_layer = nn.Conv2d(64, out_classes, kernel_size=1)

    def forward(self, x):
        # Encoder
        c1 = self.conv1(x)
        d1 = self.down1(c1)
        
        c2 = self.conv2(d1)
        d2 = self.down2(c2)
        
        # Bottleneck Dilations
        b1 = self.dilated1(d2)
        b2 = self.dilated2(b1)
        b3 = self.dilated3(b2)
        
        # Decoder 1 (merge with c2)
        # b3 has 128 channels. Max pool was 2x down. We upsample.
        u1 = F.interpolate(b3, scale_factor=2, mode='bilinear', align_corners=True)
        m1 = torch.cat([u1, c2], dim=1) # 128 + 128 = 256 channels
        dec1_conv = DoubleConv(256, 128).to(x.device)(m1)

        # Decoder 2 (merge with c1)
        u2 = F.interpolate(dec1_conv, scale_factor=2, mode='bilinear', align_corners=True)
        m2 = torch.cat([u2, c1], dim=1) # 128 + 64 = 192 channels
        dec2_conv = DoubleConv(192, 64).to(x.device)(m2)

        return self.out_layer(dec2_conv)


# Custom remote-sensing loss function
class DiceBCELoss(nn.Module):
    def __init__(self, weight=None, size_average=True):
        super(DiceBCELoss, self).__init__()

    def forward(self, inputs, targets, smooth=1):
        # inputs: [B, C, H, W] - raw logits
        # targets: [B, H, W] - class indices
        num_classes = inputs.size(1)
        targets_one_hot = F.one_hot(targets, num_classes).permute(0, 3, 1, 2).float()
        
        inputs_softmax = F.softmax(inputs, dim=1)
        
        # Cross Entropy
        ce_loss = F.cross_entropy(inputs, targets, reduction='mean')
        
        # Dice Loss per class
        dice_loss = 0.0
        for c in range(num_classes):
            if_flat = inputs_softmax[:, c, :, :].contiguous().view(-1)
            tg_flat = targets_one_hot[:, c, :, :].contiguous().view(-1)
            
            intersection = (if_flat * tg_flat).sum()
            dice = (2.*intersection + smooth) / (if_flat.sum() + tg_flat.sum() + smooth)
            dice_loss += (1 - dice)
            
        return ce_loss + (dice_loss / num_classes)
