import torch

def standardize(Y: torch.Tensor):
    stddim = -1 if Y.dim() < 2 else -2
    Y_std = Y.std(dim=stddim, keepdim=True)
    Y_std = Y_std.where(Y_std >= 1e-9, torch.full_like(Y_std, 1.0))
    Y_mean = Y.mean(dim=stddim, keepdim=True)
    return (Y - Y_mean) / Y_std, Y_mean, Y_std

def unstandardize(Y: torch.Tensor, Y_mean, Y_std):
    return Y * Y_std + Y_mean

def normalize(i: torch.Tensor):
    min = i.min(dim=0)[0]
    max = i.max(dim=0)[0]
    print("min, max")
    print(min, max)
    return (i - min) / (max - min), min, max


def unnormalize(i, min, max):
    return i * (max - min) + min