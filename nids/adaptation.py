"""FedAvg simulation and label-gated online learning utilities."""
import copy
import numpy as np
import torch


def fedavg(states,counts):
    if not states or len(states)!=len(counts) or min(counts)<=0:
        raise ValueError('Provide client states and positive sample counts')
    total=sum(counts)
    return {k:sum(s[k]*n/total for s,n in zip(states,counts))
            if states[0][k].is_floating_point() else states[0][k].clone()
            for k in states[0]}


def local_update(model,x,y,epochs=1,lr=.001):
    if len(x)!=len(y) or len(y)==0: raise ValueError('Labeled samples required')
    local=copy.deepcopy(model);local.train();opt=torch.optim.AdamW(local.parameters(),lr=lr)
    for _ in range(epochs):
        for ids in torch.randperm(len(x)).split(128):
            opt.zero_grad();loss=torch.nn.functional.cross_entropy(local(x[ids]),y[ids])
            loss.backward();torch.nn.utils.clip_grad_norm_(local.parameters(),1);opt.step()
    return local


class PageHinkley:
    """Streaming loss-increase detector; requires delayed ground-truth labels."""
    def __init__(self,delta=.005,threshold=5):
        self.delta=delta;self.threshold=threshold;self.reset()
    def reset(self): self.n=0;self.mean=0.;self.total=0.;self.minimum=0.
    def update(self,value):
        if not np.isfinite(value):raise ValueError('Finite observed loss required')
        self.n+=1;self.mean+=(value-self.mean)/self.n
        self.total+=value-self.mean-self.delta;self.minimum=min(self.minimum,self.total)
        drift=self.total-self.minimum>self.threshold
        if drift:self.reset()
        return drift
