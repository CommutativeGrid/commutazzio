import numpy as np
def radii_generator(start,end,ladder_length):
    """Return a list of radius based on the input values."""
    radia=np.linspace(start,end,ladder_length)
    return radia