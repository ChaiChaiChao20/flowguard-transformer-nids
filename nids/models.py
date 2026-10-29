"""Feature attention and comparable fixed-feature-order neural baselines."""
import torch
from torch import nn


class FeatureTransformer(nn.Module):
    def __init__(self, features, classes, dim=32, heads=4, layers=2, dropout=0.1):
        super().__init__()
        if dim % heads:
            raise ValueError("Embedding dimension must be divisible by attention heads.")
        # Per-feature affine value tokenization (FT-Transformer-inspired).
        self.weight = nn.Parameter(torch.randn(features, dim) * 0.02)
        self.identity = nn.Parameter(torch.randn(features, dim) * 0.02)
        self.cls = nn.Parameter(torch.randn(1, 1, dim) * 0.02)
        layer = nn.TransformerEncoderLayer(
            d_model=dim, nhead=heads, dim_feedforward=dim*4,
            dropout=dropout, batch_first=True, activation="gelu", norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=layers, enable_nested_tensor=False)
        self.head = nn.Sequential(nn.LayerNorm(dim), nn.Linear(dim, classes))

    def forward(self, x):
        tokens = x.unsqueeze(-1) * self.weight + self.identity
        tokens = torch.cat([self.cls.expand(x.shape[0], -1, -1), tokens], dim=1)
        return self.head(self.encoder(tokens)[:, 0])


class MLP(nn.Module):
    def __init__(self, features, classes, **kwargs):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(features, 128), nn.GELU(), nn.Dropout(0.1),
                                 nn.Linear(128, 128), nn.GELU(), nn.Linear(128, classes))

    def forward(self, x):
        return self.net(x)


class CNN(nn.Module):
    def __init__(self, features, classes, **kwargs):
        super().__init__()
        self.conv = nn.Sequential(nn.Conv1d(1, 32, 3, padding=1), nn.GELU(),
                                  nn.Conv1d(32, 32, 3, padding=1), nn.GELU())
        self.head = nn.Sequential(nn.Flatten(), nn.Linear(32*features, 64), nn.GELU(),
                                  nn.Dropout(0.1), nn.Linear(64, classes))

    def forward(self, x):
        return self.head(self.conv(x.unsqueeze(1)))


class Recurrent(nn.Module):
    def __init__(self, features, classes, kind="LSTM", **kwargs):
        super().__init__()
        # Fixed feature order; this is not a chronological traffic sequence.
        self.rnn = getattr(nn, kind)(input_size=1, hidden_size=48, batch_first=True)
        self.head = nn.Linear(48*features, classes)

    def forward(self, x):
        out, _ = self.rnn(x.unsqueeze(-1))
        return self.head(out.flatten(1))


def build_model(name, features, classes, **config):
    if name == "Transformer":
        return FeatureTransformer(features, classes, **config)
    if name == "MLP":
        return MLP(features, classes)
    if name == "CNN":
        return CNN(features, classes)
    if name in {"LSTM", "GRU"}:
        return Recurrent(features, classes, kind=name)
    raise ValueError(f"Unknown model: {name}")

