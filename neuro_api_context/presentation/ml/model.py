import torch
from torch import nn


class UNetDown(nn.Module):
    def __init__(self, in_size, out_size, normalize=True):
        super().__init__()
        layers = [nn.Conv2d(in_size, out_size, 4, 2, 1, bias=False)]
        if normalize:
            layers.append(nn.BatchNorm2d(out_size))
        layers.append(nn.LeakyReLU(0.2, inplace=True))
        self.model = nn.Sequential(*layers)

    def forward(self, x):
        return self.model(x)


class GeneratorUNet(nn.Module):
    def __init__(self, in_channels=15, out_channels=13):
        super().__init__()
        # Downsampling
        self.down1 = UNetDown(in_channels, 64, normalize=False)  # 15->64
        self.down2 = UNetDown(64, 128)  # 64->128
        self.down3 = UNetDown(128, 256)  # 128->256
        self.down4 = UNetDown(256, 512)  # 256->512
        # Upsampling
        self.up1 = UNetUp(512, 256, dropout=0.5)  # 512->256, concat 256->512
        self.up2 = UNetUp(512, 128, dropout=0.5)  # 512->128, concat 128->256
        self.up3 = UNetUp(256, 64)  # 256->64, concat 64->128
        # Final layer
        self.final = nn.Sequential(nn.ConvTranspose2d(128, out_channels, 4, 2, 1), nn.Tanh())
        self.apply(self.init_weights)

    def init_weights(self, net, init_type="normal", mean=0.0, std=0.02):
        for m in net.modules():
            if isinstance(m, (nn.Conv2d, nn.ConvTranspose2d, nn.BatchNorm2d)):
                nn.init.normal_(m.weight.data, mean, std)
                if m.bias is not None:
                    nn.init.constant_(m.bias.data, 0)

    def forward(self, x):
        d1 = self.down1(x)
        d2 = self.down2(d1)
        d3 = self.down3(d2)
        d4 = self.down4(d3)

        u1 = self.up1(d4, d3)
        u2 = self.up2(u1, d2)
        u3 = self.up3(u2, d1)
        return self.final(u3)


# U-Net upsampling block
class UNetUp(nn.Module):
    def __init__(self, in_size, out_size, dropout=0.0):
        super().__init__()
        layers = [
            nn.ConvTranspose2d(in_size, out_size, 4, 2, 1, bias=False),
            nn.BatchNorm2d(out_size),
            nn.ReLU(inplace=True),
        ]
        if dropout:
            layers.append(nn.Dropout(dropout))
        self.model = nn.Sequential(*layers)

    def forward(self, x, skip_input):
        x = self.model(x)
        # concat with skip connection
        return torch.cat([x, skip_input], dim=1)
