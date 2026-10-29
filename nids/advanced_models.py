"""Optional architectures from the brief, with explicit input contracts."""
import torch
from torch import nn


class TemporalTransformer(nn.Module):
    """Causal encoder over chronological flows; output labels the last flow."""
    def __init__(self, features, classes, dim=32, heads=4, layers=2, window=8):
        super().__init__()
        self.window=window
        self.project=nn.Linear(features,dim)
        self.position=nn.Parameter(torch.randn(window,dim)*.02)
        layer=nn.TransformerEncoderLayer(dim,heads,dim*4,.1,batch_first=True,
                                         activation='gelu',norm_first=True)
        self.encoder=nn.TransformerEncoder(layer,layers,enable_nested_tensor=False)
        self.head=nn.Sequential(nn.LayerNorm(dim),nn.Linear(dim,classes))

    def forward(self,x):
        if x.ndim!=3 or x.shape[1]>self.window:
            raise ValueError('Expected [batch, chronological time, features] within configured window')
        t=x.shape[1]
        mask=torch.triu(torch.ones(t,t,dtype=torch.bool,device=x.device),diagonal=1)
        h=self.encoder(self.project(x)+self.position[:t],mask=mask)
        return self.head(h[:,-1])


class FlowViT(nn.Module):
    """Flow feature grid -> six four-value patches -> vision-style encoder.

    This numerical grid is a representation choice, not a packet image.
    """
    def __init__(self,features,classes,dim=32):
        super().__init__()
        self.features=features;self.patches=(features+3)//4
        self.patch=nn.Linear(4,dim)
        self.position=nn.Parameter(torch.randn(1,self.patches,dim)*.02)
        self.cls=nn.Parameter(torch.zeros(1,1,dim))
        layer=nn.TransformerEncoderLayer(dim,4,dim*4,.1,batch_first=True,activation='gelu')
        self.encoder=nn.TransformerEncoder(layer,2)
        self.head=nn.Linear(dim,classes)

    def forward(self,x):
        x=nn.functional.pad(x,(0,self.patches*4-self.features)).reshape(-1,self.patches,4)
        h=self.patch(x)+self.position
        return self.head(self.encoder(torch.cat([self.cls.expand(len(x),-1,-1),h],1))[:,0])


class TabTransformer(nn.Module):
    """Contextual categorical tokens + numeric MLP, as mixed tabular input."""
    def __init__(self,features,classes,cardinalities=(4,8),dim=16):
        super().__init__()
        self.embeddings=nn.ModuleList([nn.Embedding(c,dim) for c in cardinalities])
        layer=nn.TransformerEncoderLayer(dim,4,dim*4,.1,batch_first=True,activation='gelu')
        self.encoder=nn.TransformerEncoder(layer,2)
        self.head=nn.Sequential(nn.Linear(features+len(cardinalities)*dim,64),nn.GELU(),nn.Linear(64,classes))

    def forward(self,x,categories):
        tokens=torch.stack([e(categories[:,i]) for i,e in enumerate(self.embeddings)],1)
        return self.head(torch.cat([x,self.encoder(tokens).flatten(1)],1))


class FlowGraphNetwork(nn.Module):
    """Two-layer GCN on flows connected by a shared endpoint in one window."""
    def __init__(self,features,classes,dim=32):
        super().__init__();self.first=nn.Linear(features,dim);self.second=nn.Linear(dim,classes)

    def forward(self,x,adjacency):
        degree=adjacency.sum(-1).clamp_min(1)
        norm=adjacency/torch.sqrt(degree[:,None]*degree[None,:])
        return norm @ self.second(torch.relu(norm @ self.first(x)))


def build_advanced(name,features,classes):
    if name=='TemporalTransformer': return TemporalTransformer(features,classes)
    if name=='FlowViT': return FlowViT(features,classes)
    if name=='TabTransformer': return TabTransformer(features,classes)
    if name=='FlowGraphNetwork': return FlowGraphNetwork(features,classes)
    if name=='BERTStyleEncoder':
        # CLS bidirectional feature encoder, randomly initialized; no NLP BERT weights.
        from .models import FeatureTransformer
        return FeatureTransformer(features,classes)
    raise ValueError(name)
