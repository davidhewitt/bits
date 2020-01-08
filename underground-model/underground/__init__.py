from .model import Model
from .parse import parse_dlr, parse_underground

def make_standard_model():
    """Make the standard underground + DLR model."""
    model = Model()
    parse_underground("underground.html", model)
    parse_dlr("dlr.html", model)
    return model
