"""
Finish the code according to the following latex code:

"""

from .aggregate_dimension import cl4_isoclasses_agg_dict
import numpy as np
from functools import lru_cache


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
        self.decomp = {L: mult for L, mult in decomp.items() if mult > 0}
        self.decomp = {L: mult for L, mult in decomp.items()}
        if not self.decomp:
            raise ValueError("The decomposition is empty.")
        self.non_int_comp = {L: multi for L, multi in self.decomp.items() if L[0] == 'N'}
        self.iso_agg = {L: cl4_isoclasses_agg_dict[L] for L in self.decomp}
        self.agg = sum(multi * self.iso_agg[L] for L, multi in self.decomp.items())
        if self.agg == 0:
            raise ValueError("Should not happen.")
        self.agg_N = sum(multi * self.iso_agg[N] for N, multi in self.non_int_comp.items())

    @property
    def ns_const(self):
        """
        Compute n-Score_c
        """
        return self.agg_N / self.agg

    @lru_cache(maxsize=32)
    def ns_logistic(self,d0):
        """
        Compute the non-interval score 
        using the logistic function to assign the weights.
        d0 for offset.
        """
        weights = {L: 1 / (1 + np.exp(-(self.decomp[L] - d0))) for L in self.decomp}
        numerator = sum(mult * weights[N] * self.iso_agg[N] for N, mult in self.non_int_comp.items())
        denominator = sum(mult * weights[L] * self.iso_agg[L] for L, mult in self.decomp.items())
        # print(weights)
        # print(numerator,denominator)
        if denominator == 0:
            raise ValueError("Encountered division by zero in ns_logistic.")
        return numerator / denominator
    

