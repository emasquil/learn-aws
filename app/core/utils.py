import torch
from torch import nn
from torchvision import models as torchvision_models


def load_model(checkpoint_path: str, device: str = "cpu") -> nn.Module:
    """
    Instantiates the PyTorch model and loads the checkpoint indicated by
    `checkpoint_path`. The model is put on eval mode and assigned to the specified
    `device`.
    Model taken from: https://github.com/amitrajitbose/cat-v-dog-classifier-pytorch

    Arguments:
        checkpoint_path {str} -- Path to the file containing the saved model weights.

    Keyword Arguments:
        device {str} -- Device to assign the model to (default: {"cpu"}).

    Returns:
        nn.Module -- The loaded PyTorch model.
    """
    device = torch.device(device)
    checkpoint = torch.load(checkpoint_path, map_location=device)

    model = torchvision_models.densenet121(pretrained=False)
    model.classifier = nn.Sequential(
        nn.Linear(1024, 512),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(512, 256),
        nn.ReLU(),
        nn.Dropout(0.1),
        nn.Linear(256, 2),
        nn.LogSoftmax(dim=1),
    )
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    return model
