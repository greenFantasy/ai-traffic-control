import torch

def mse(model, dl):
    model.eval()
    total_se = 0
    total = 0
    for states, actions, values in dl:
        pred_values = torch.gather(model(states), dim=1, index=actions.unsqueeze(1)).squeeze(1)
        total_se += (pred_values - values).pow(2).sum().item()
        total += len(states)
    return total_se / total

def mae(model, dl):
    model.eval()
    total_diff = 0
    total = 0
    for states, actions, values in dl:
        pred_values = torch.gather(model(states), dim=1, index=actions.unsqueeze(1)).squeeze(1)
        total_diff += (pred_values - values).abs().sum().item()
        total += len(states)
    return total_diff / total

def min_pred(model, dl):
    model.eval()
    m = float('inf')
    for states, actions, values in dl:
        pred_values = torch.gather(model(states), dim=1, index=actions.unsqueeze(1)).squeeze(1)
        m = min(m, torch.min(pred_values).item())
    return m

def max_pred(model, dl):
    model.eval()
    m = -float('inf')
    for states, actions, values in dl:
        pred_values = torch.gather(model(states), dim=1, index=actions.unsqueeze(1)).squeeze(1)
        m = max(m, torch.max(pred_values).item())
    return m

def average_pred(model, dl):
    model.eval()
    total_sum = 0
    total = 0
    for states, actions, values in dl:
        pred_values = torch.gather(model(states), dim=1, index=actions.unsqueeze(1)).squeeze(1)
        total_sum += pred_values.sum()
        total += len(states)
    return total_sum / total