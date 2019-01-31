import torch
from torch.nn.parameter import Parameter
from torch.nn import functional as F
from torch.nn.modules.conv import _ConvNd
from torch.nn.modules.utils import _pair
import torch.nn as nn
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


class GaborSmallConv2d(_ConvNd):

    def __init__(self, in_channels, out_channels, kernel_size, stride=1,
                 padding=0, dilation=1, groups=1, bias=False):
        kernel_size = _pair(kernel_size)
        stride = _pair(stride)
        padding = _pair(padding)
        dilation = _pair(dilation)

        super(GaborSmallConv2d, self).__init__(in_channels, out_channels, kernel_size, stride, padding, dilation, False, _pair(0), groups, bias)
        # TODO: подумать над инициализацией параметров
        self.sigma_x = nn.Parameter(0.5*torch.rand(out_channels, in_channels))
        self.sigma_y = nn.Parameter(0.5*torch.rand(out_channels, in_channels))
        self.freq = nn.Parameter((kernel_size[0]/2)*torch.rand(out_channels, in_channels))
        self.theta = nn.Parameter(3.14*torch.rand(out_channels, in_channels))
        self.psi = nn.Parameter(6.28*torch.rand(out_channels, in_channels))

    def forward(self, input):

        y, x = torch.meshgrid([torch.linspace(-0.5, 0.5, self.kernel_size[0]), torch.linspace(-0.5, 0.5, self.kernel_size[1])])
        x = x.to(device)
        y = y.to(device)
        weight = torch.empty(self.weight.shape, requires_grad=False).to(device)
        for i in range(self.out_channels):
            for j in range(self.in_channels):
                sigma_x = self.sigma_x[i, j].expand_as(y)
                sigma_y = self.sigma_y[i, j].expand_as(y)
                freq = self.freq[i, j].expand_as(y)
                theta = self.theta[i, j].expand_as(y)
                psi = self.psi[i, j].expand_as(y)

                rotx = x * torch.cos(theta) + y * torch.sin(theta)
                roty = -x * torch.sin(theta) + y * torch.cos(theta)

                g = torch.zeros(y.shape)

                g = torch.exp(-0.5 * (rotx ** 2 / (sigma_x + 1e-3) ** 2 + roty ** 2 / (sigma_y + 1e-3) ** 2))
                g = g * torch.cos(2 * 3.14 * freq * rotx + psi)
                weight[i, j] = g
                self.weight.data[i, j] = g
        return F.conv2d(input, weight, self.bias, self.stride, self.padding, self.dilation, self.groups)


class GaborConv2d(_ConvNd):

    def __init__(self, in_channels, out_channels, kernel_size, stride=1,
                 padding=0, dilation=1, groups=1, bias=False):
        kernel_size = _pair(kernel_size)
        stride = _pair(stride)
        padding = _pair(padding)
        dilation = _pair(dilation)

        super(GaborConv2d, self).__init__(in_channels, out_channels, kernel_size, stride, padding, dilation, False, _pair(0), groups, bias)
        # TODO: подумать над инициализацией параметров
        self.sigma_x = nn.Parameter(0.5*torch.rand(out_channels, in_channels))
        self.sigma_y = nn.Parameter(0.5*torch.rand(out_channels, in_channels))
        self.freq = nn.Parameter((kernel_size[0]/2)*torch.rand(out_channels, in_channels))
        self.theta = nn.Parameter(3.14*torch.rand(out_channels, in_channels))
        self.theta2 = nn.Parameter(3.14*torch.rand(out_channels, in_channels))
        self.psi = nn.Parameter(6.28*torch.rand(out_channels, in_channels))

    def forward(self, input):

        y, x = torch.meshgrid([torch.linspace(-0.5, 0.5, self.kernel_size[0]), torch.linspace(-0.5, 0.5, self.kernel_size[1])])
        x = x.to(device)
        y = y.to(device)
        weight = torch.empty(self.weight.shape, requires_grad=False).to(device)
        for i in range(self.out_channels):
            for j in range(self.in_channels):
                sigma_x = self.sigma_x[i, j].expand_as(y)
                sigma_y = self.sigma_y[i, j].expand_as(y)
                freq = self.freq[i, j].expand_as(y)
                theta = self.theta[i, j].expand_as(y)
                theta2 = self.theta2[i, j].expand_as(y)
                psi = self.psi[i, j].expand_as(y)

                rotx = x * torch.cos(theta) + y * torch.sin(theta)
                roty = -x * torch.sin(theta) + y * torch.cos(theta)

                g = torch.zeros(y.shape)

                g = torch.exp(-0.5 * (rotx ** 2 / (sigma_x + 1e-3) ** 2 + roty ** 2 / (sigma_y + 1e-3) ** 2))
                g = g * torch.cos(2 * 3.14 * (freq * x * torch.cos(theta2) + freq * y * torch.sin(theta2)) + psi)
                weight[i, j] = g
                self.weight.data[i, j] = g
        return F.conv2d(input, weight, self.bias, self.stride, self.padding, self.dilation, self.groups)


class GaborCurvedConv2d(_ConvNd):

    def __init__(self, in_channels, out_channels, kernel_size, stride=1,
                 padding=0, dilation=1, groups=1, bias=False):
        kernel_size = _pair(kernel_size)
        stride = _pair(stride)
        padding = _pair(padding)
        dilation = _pair(dilation)

        super(GaborCurvedConv2d, self).__init__(in_channels, out_channels, kernel_size, stride, padding, dilation, False, _pair(0), groups, bias)

        # TODO: подумать над инициализацией параметров
        self.sigma_x = nn.Parameter(0.5*torch.rand(out_channels, in_channels))
        self.sigma_y = nn.Parameter(0.5*torch.rand(out_channels, in_channels))
        self.freq = nn.Parameter(kernel_size[0]/2 * torch.rand(out_channels, in_channels))
        self.theta = nn.Parameter(3.14*torch.rand(out_channels, in_channels))
        self.theta2 = nn.Parameter(6.28*torch.rand(out_channels, in_channels))
        self.psi = nn.Parameter(6.28*torch.rand(out_channels, in_channels))
        self.rad = nn.Parameter(1 + torch.rand(out_channels, in_channels))
        self.center_x = nn.Parameter(2*torch.rand(out_channels, in_channels) - 1)
        self.center_y = nn.Parameter(2*torch.rand(out_channels, in_channels) - 1)

    def forward(self, input):

        y, x = torch.meshgrid([torch.linspace(-0.5, 0.5, self.kernel_size[0]), torch.linspace(-0.5, 0.5, self.kernel_size[1])])
        x = x.to(device)
        y = y.to(device)
        weight = torch.empty(self.weight.shape, requires_grad=False).to(device)
        for i in range(self.out_channels):
            for j in range(self.in_channels):
                sigma_x = self.sigma_x[i, j].expand_as(y)
                sigma_y = self.sigma_y[i, j].expand_as(y)
                freq = self.freq[i, j].expand_as(y)
                theta = self.theta[i, j].expand_as(y)
                psi = self.psi[i, j].expand_as(y)

                cx = (self.center_x[i, j] - self.rad[i, j]*torch.cos(self.theta2[i, j])).expand_as(y)
                cy = (self.center_y[i, j] - self.rad[i, j]*torch.sin(self.theta2[i, j])).expand_as(y)
                r = ((x - cx)**2 + (y - cy)**2)**(1/2)

                rotx = x * torch.cos(theta) + y * torch.sin(theta)
                roty = -x * torch.sin(theta) + y * torch.cos(theta)

                g = torch.zeros(y.shape)
                g = torch.exp(-0.5 * (rotx ** 2 / (sigma_x + 1e-3) ** 2 + roty ** 2 / (sigma_y + 1e-3) ** 2))
                g = g * torch.cos(2 * 3.14 * freq * r + psi)

                weight[i, j] = g
                self.weight.data[i, j] = g
        return F.conv2d(input, weight, self.bias, self.stride, self.padding, self.dilation, self.groups)