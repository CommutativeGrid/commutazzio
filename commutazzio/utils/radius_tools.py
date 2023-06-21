import numpy as np
def radii_generator(start,end,ladder_length):
    """Return a list of radius based on the input values."""
    radii=np.linspace(start,end,ladder_length)
    return radii



def join_and_unique(arr1, arr2, precision=3):
    arr = np.concatenate((arr1, arr2))
    arr_rounded = np.around(arr, decimals=precision)
    unique_rounded, indices = np.unique(arr_rounded, return_index=True)
    return np.sort(arr[indices])



