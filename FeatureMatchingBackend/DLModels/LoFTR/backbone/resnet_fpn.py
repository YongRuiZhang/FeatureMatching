import torch.nn as nn
import torch.nn.functional as F


def conv1x1(in_planes, out_planes, stride=1):
    """1x1 convolution without padding"""
    return nn.Conv2d(in_planes, out_planes, kernel_size=1, stride=stride, padding=0, bias=False)


def conv3x3(in_planes, out_planes, stride=1):
    """3x3 convolution with padding"""
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride, padding=1, bias=False)


class BasicBlock(nn.Module):
    def __init__(self, in_planes, planes, stride=1):
        super().__init__()
        self.conv1 = conv3x3(in_planes, planes, stride)
        self.conv2 = conv3x3(planes, planes)
        self.bn1 = nn.BatchNorm2d(planes)
        self.bn2 = nn.BatchNorm2d(planes)
        self.relu = nn.ReLU(inplace=True)

        if stride == 1:
            self.downsample = None
        else:
            self.downsample = nn.Sequential(
                conv1x1(in_planes, planes, stride=stride),
                nn.BatchNorm2d(planes)
            )

    def forward(self, x):
        y = x
        y = self.relu(self.bn1(self.conv1(y)))
        y = self.bn2(self.conv2(y))

        if self.downsample is not None:
            x = self.downsample(x)

        return self.relu(x+y)


class ResNetFPN_8_2(nn.Module):
    """
    ResNet+FPN, output resolution are 1/8 and 1/2.
    Each block has 2 layers.
    """

    def __init__(self, config):
        super().__init__()
        # Config
        block = BasicBlock
        initial_dim = config['initial_dim']  # 128
        block_dims = config['block_dims']  # [128, 196, 256]

        # Class Variable
        self.in_planes = initial_dim  # 128

        # Networks
        self.conv1 = nn.Conv2d(1, initial_dim, kernel_size=7, stride=2, padding=3, bias=False)  # (N, 128, H/2, W/2)
        self.bn1 = nn.BatchNorm2d(initial_dim)
        self.relu = nn.ReLU(inplace=True)

        self.layer1 = self._make_layer(block, block_dims[0], stride=1)  # 1/2  (N, 128, H/2, W/2) 实际经过两次 self.relu(x+y)，不变换尺寸
        self.layer2 = self._make_layer(block, block_dims[1], stride=2)  # 1/4  (N, 196, H/4, W/4)
        self.layer3 = self._make_layer(block, block_dims[2], stride=2)  # 1/8  (N, 256, H/8, W/8)

        # 3. FPN upsample
        self.layer3_outconv = conv1x1(block_dims[2], block_dims[2])  # (N, 256, H/8, W/8) -> (N, 256, H/8, W/8)
        self.layer2_outconv = conv1x1(block_dims[1], block_dims[2])  # (N, 196, H/8, W/8) -> (N, 256, H/8, W/8)
        self.layer2_outconv2 = nn.Sequential(
            conv3x3(block_dims[2], block_dims[2]),  # (N, 256, H/8, W/8) -> (N, 256, H/8, W/8)
            nn.BatchNorm2d(block_dims[2]),
            nn.LeakyReLU(),
            conv3x3(block_dims[2], block_dims[1]),  # (N, 256, H/8, W/8) -> (N, 196, H/8, W/8)
        )
        self.layer1_outconv = conv1x1(block_dims[0], block_dims[1])  # (N, 128, H/8, W/8) -> (N, 196, H/8, W/8)
        self.layer1_outconv2 = nn.Sequential(
            conv3x3(block_dims[1], block_dims[1]),  # (N, 196, H/8, W/8) -> (N, 196, H/8, W/8)
            nn.BatchNorm2d(block_dims[1]),
            nn.LeakyReLU(),
            conv3x3(block_dims[1], block_dims[0]),  # (N, 196, H/8, W/8) -> (N, 128, H/8, W/8)
        )

        # 初始化 模型中的所有模块
        for m in self.modules():
            if isinstance(m, nn.Conv2d):  # 如果当前模块是卷积层
                # 使用 Kaiming 正态分布初始化卷积层的权重
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, (nn.BatchNorm2d, nn.GroupNorm)):  # 如果当前模块是批量归一化层或组归一化层
                nn.init.constant_(m.weight, 1)  # 将权重初始化为1
                nn.init.constant_(m.bias, 0)  # 将偏置项初始化为0

    def _make_layer(self, block, dim, stride=1):
        layer1 = block(self.in_planes, dim, stride=stride)  # 下采样
        layer2 = block(dim, dim, stride=1)  # self.relu(x+y)
        layers = (layer1, layer2)

        self.in_planes = dim
        return nn.Sequential(*layers)

    def forward(self, x):
        """ x: (N, 1, H, W) , 其中也可能是 (2*N, 1, H, W), 但第一个维度不参与计算，无影响"""
        # ResNet Backbone
        x0 = self.relu(self.bn1(self.conv1(x)))  # self.conv1(x): (N, 1, H, W) ->  (N, 128, H/2, W/2)
        x1 = self.layer1(x0)  # 1/2  实际经过两次 BasicBlock的 self.relu(x+y)，不变换尺寸
        x2 = self.layer2(x1)  # 1/4  (N, 128, H/2, W/2) -> (N, 196, H/4, W/4)
        x3 = self.layer3(x2)  # 1/8  (N, 196, H/4, W/4) -> (N, 256, H/8, W/8)

        # FPN
        x3_out = self.layer3_outconv(x3)  # (N, 256, H/8, W/8) -> (N, 256, H/8, W/8)

        x3_out_2x = F.interpolate(x3_out, scale_factor=2., mode='bilinear', align_corners=True)  # 将输入张量的大小放大2倍（scale_factor=2.），并使用 双线性插值法 进行插值计算  (N, 256, H/8, W/8) -> (N, 256, H/4, W/4)
        x2_out = self.layer2_outconv(x2)  # (N, 196, H/4, W/4) -> (N, 256, H/4, W/4)
        x2_out = self.layer2_outconv2(x2_out+x3_out_2x)  # (N, 256, H/4, W/4) -> (N, 196, H/4, W/4)

        x2_out_2x = F.interpolate(x2_out, scale_factor=2., mode='bilinear', align_corners=True)  # (N, 196, H/4, W/4) -> (N, 196, H/2, W/2)
        x1_out = self.layer1_outconv(x1)  # (N, 128, H/2, W/2) -> (N, 196, H/2, W/2)
        x1_out = self.layer1_outconv2(x1_out+x2_out_2x)  # (N, 196, H/2, W/2) -> (N, 196, H/2, W/2)

        return [x3_out, x1_out]  # 分别返回的是 1/8尺度的特征 以及 1/2的特征


class ResNetFPN_16_4(nn.Module):
    """
    ResNet+FPN, output resolution are 1/16 and 1/4.
    Each block has 2 layers.
    """

    def __init__(self, config):
        super().__init__()
        # Config
        block = BasicBlock
        initial_dim = config['initial_dim']
        block_dims = config['block_dims']

        # Class Variable
        self.in_planes = initial_dim

        # Networks
        self.conv1 = nn.Conv2d(1, initial_dim, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(initial_dim)
        self.relu = nn.ReLU(inplace=True)

        self.layer1 = self._make_layer(block, block_dims[0], stride=1)  # 1/2
        self.layer2 = self._make_layer(block, block_dims[1], stride=2)  # 1/4
        self.layer3 = self._make_layer(block, block_dims[2], stride=2)  # 1/8
        self.layer4 = self._make_layer(block, block_dims[3], stride=2)  # 1/16

        # 3. FPN upsample
        self.layer4_outconv = conv1x1(block_dims[3], block_dims[3])
        self.layer3_outconv = conv1x1(block_dims[2], block_dims[3])
        self.layer3_outconv2 = nn.Sequential(
            conv3x3(block_dims[3], block_dims[3]),
            nn.BatchNorm2d(block_dims[3]),
            nn.LeakyReLU(),
            conv3x3(block_dims[3], block_dims[2]),
        )

        self.layer2_outconv = conv1x1(block_dims[1], block_dims[2])
        self.layer2_outconv2 = nn.Sequential(
            conv3x3(block_dims[2], block_dims[2]),
            nn.BatchNorm2d(block_dims[2]),
            nn.LeakyReLU(),
            conv3x3(block_dims[2], block_dims[1]),
        )

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, (nn.BatchNorm2d, nn.GroupNorm)):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

    def _make_layer(self, block, dim, stride=1):
        layer1 = block(self.in_planes, dim, stride=stride)
        layer2 = block(dim, dim, stride=1)
        layers = (layer1, layer2)

        self.in_planes = dim
        return nn.Sequential(*layers)

    def forward(self, x):
        # ResNet Backbone
        x0 = self.relu(self.bn1(self.conv1(x)))
        x1 = self.layer1(x0)  # 1/2
        x2 = self.layer2(x1)  # 1/4
        x3 = self.layer3(x2)  # 1/8
        x4 = self.layer4(x3)  # 1/16

        # FPN
        x4_out = self.layer4_outconv(x4)

        x4_out_2x = F.interpolate(x4_out, scale_factor=2., mode='bilinear', align_corners=True)
        x3_out = self.layer3_outconv(x3)
        x3_out = self.layer3_outconv2(x3_out+x4_out_2x)

        x3_out_2x = F.interpolate(x3_out, scale_factor=2., mode='bilinear', align_corners=True)
        x2_out = self.layer2_outconv(x2)
        x2_out = self.layer2_outconv2(x2_out+x3_out_2x)

        return [x4_out, x2_out]
