"""
Finish the code according to the following latex code:

"""

from .aggregate_dimension import cl4_isoclasses_agg_array
import numpy as np
from functools import lru_cache
from collections import OrderedDict
from numba import njit


@njit
def logistic(x:np.array, d0:float):
    return 1 / (1 + np.exp(-(x - d0)))

class CL4_NIScores:
    """
    A class to calculate the non-interval scores of
    from the total decomposition of a CL4 representation.
    """

    def __init__(self, decomp:dict):
        """
        Initialize the class with the total decomposition of the CL4 model.
        """
        # only keep non-zero entries, save as numpy array
        Is=[f"I{_}" for _ in range(1, 56)]
        Ns=[f"N{_}" for _ in range(1, 22)]
        Ls=Is + Ns
        # make decomp an ordered dict, in the order of Ls
        ordered_decomp = OrderedDict((k, decomp.get(k, 0)) for k in Ls)
        self.decomp = np.array(list(ordered_decomp.values()))
        # if all zeros, raise error
        if not np.any(self.decomp):
            raise ValueError("The decomposition is empty.")
        self.iso_agg = cl4_isoclasses_agg_array
        self.agg = np.sum(self.decomp * self.iso_agg)
        if self.agg == 0:
            raise ValueError("Should not happen.")
        self.agg_N = np.sum(self.decomp[55:] * self.iso_agg[55:])


    @property
    def ns_const(self):
        """
        Compute n-Score_c
        """
        return self.agg_N / self.agg

    @staticmethod
    @njit
    def ns_logistic_numba(decomp,iso_agg,d0):
        """
        Compute the non-interval score 
        using the logistic function to assign the weights.
        d0 for offset.
        """
        weights = logistic(decomp, d0)
        numerator = np.sum(decomp[55:]*weights[55:]*iso_agg[55:])
        denominator = np.sum(decomp * weights * iso_agg)
        # print(weights)
        # print(numerator,denominator)
        if denominator == 0:
            raise ValueError("Encountered division by zero in ns_logistic.")
        return numerator / denominator
    
    @lru_cache(maxsize=32)
    def ns_logistic(self,d0):
        return self.ns_logistic_numba(self.decomp,self.iso_agg,d0)