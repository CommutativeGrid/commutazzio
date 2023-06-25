"""
Finish the code according to the following latex code:

"""

from .aggregate_dimension import cl4_isoclasses_agg_array
import numpy as np
from functools import lru_cache
from collections import OrderedDict
from numba import njit, vectorize


import warnings
from numba import NumbaExperimentalFeatureWarning

# Ignore warnings about experimental features in Numba
warnings.filterwarnings('ignore', category=NumbaExperimentalFeatureWarning)





@vectorize(['float64(float64,float64)', 'float64(int64,int64)', 'float64(int64,float64)'])
def logistic(x:np.array, d0:float):
    return 1 / (1 + np.exp(-(x - d0)))

# weights is a list of length 11
# load weights[i] from ./weights/weight_i.npy
# ./ relative to the directory of this file, get the directory of this file by
# concatenate os.path.dirname(os.path.abspath(__file__)) with weights/weight_{i}.npy
import os
weights_precomputed = np.load(\
    os.path.join(os.path.dirname(os.path.abspath(__file__)),'weights','weights_0_to_10.npy')\
)


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
    def _ns_logistic_numba(decomp,iso_agg,d0):
        """
        Compute the non-interval score 
        using the logistic function to assign the weights.
        d0 for offset.
        """
        if d0 in [0,1,2,3,4,5,6,7,8,9,10,11]:
            weights = weights_precomputed[int(d0)]
        else:
            weights = logistic(iso_agg, d0)
        numerator = np.sum(decomp[55:]*weights[55:]*iso_agg[55:])
        denominator = np.sum(decomp * weights * iso_agg)
        # print(weights)
        # print(numerator)
        # print(denominator)
        if denominator == 0:
            raise ValueError("Encountered division by zero in ns_logistic.")
        return numerator / denominator
    
    @lru_cache(maxsize=32)
    def ns_logistic(self,d0):
        return self._ns_logistic_numba(self.decomp,self.iso_agg,d0)
    


import csv
import pandas as pd

class CLN_NIScores:
    #write prompts
    def __init__(self,dots_str:str,lines_str:str):
        """parse the dots and lines from string"""
        dots = dots_str.strip().split('\n')
        lines = lines_str.strip().split('\n')
        reader_lines = csv.DictReader(lines)
        reader_dots = csv.DictReader(dots)
        df_dots = pd.DataFrame(reader_dots)
        self.df_dots = df_dots.set_index(df_dots.columns[0])
        # set column x	y multiplicity to int, area to str
        self.df_dots['x']=self.df_dots['x'].astype(int)
        self.df_dots['y']=self.df_dots['y'].astype(int)
        self.df_dots['multiplicity']=self.df_dots['multiplicity'].astype(int)
        self.df_dots['area']=self.df_dots['area'].astype(str)
        df_lines = pd.DataFrame(reader_lines)
        #if not empty
        if not df_lines.empty:
            self.df_lines=df_lines.set_index(df_lines.columns[0])
            # set all columns to int
            self.df_lines=self.df_lines.astype(int)
        else:
            self.df_lines=pd.DataFrame(columns=['x0','y0','x1','y1','multiplicity'])

    @property
    def agg_total(self):
        """Compute the aggregate dimension of the representation"""
        # Method 1: df computations directly
        # result = np.sum(self.df_dots['multiplicity']*(self.df_dots['y']-self.df_dots['x']+1))
        # return result
        return self._agg_total_numba()
    
    def _agg_total_numba(self):
        """Compute the aggregate dimension of the representation"""
        # Method 2: numba computations
        # if area is U, b from x, d from y
        # if area is D, b from y, d from x
        b = np.where(self.df_dots['area'] == 'U', self.df_dots['x'], self.df_dots['y'])
        d = np.where(self.df_dots['area'] == 'U', self.df_dots['y'], self.df_dots['x'])
        m=np.array(self.df_dots['multiplicity'],dtype=np.int32)
        result = self._agg_total_numba_computation(b,d,m)
        return result
    
    @staticmethod
    @njit
    def _agg_total_numba_computation(b,d,m):
        """Compute the aggregate dimension of the representation"""
        # Method 2: numba computations
        return np.sum(m*(d-b+1))
    

    def _numerator_numba(self):
        b_lower= np.array(self.df_lines['y0'],dtype=np.int32)
        d_lower= np.array(self.df_lines['x0'],dtype=np.int32)
        b_upper= np.array(self.df_lines['x1'],dtype=np.int32)
        d_upper= np.array(self.df_lines['y1'],dtype=np.int32)
        m= np.array(self.df_lines['multiplicity'],dtype=np.int32)
        result = self._numerator_numba_computation(b_lower,d_lower,b_upper,d_upper,m)
        return result
    
    @property
    def ns_c_prime(self):
        return self._numerator_numba()/self._agg_total_numba()

    @staticmethod
    @njit
    def _numerator_numba_computation(b_lower,d_lower,b_upper,d_upper,m):
        """Compute the numerator of the NIScore"""
        # create a new array from m: if the entry < 0, set it to abs(entry), else set it to 0
        m=np.where(m<0,np.negative(m),0)
        return np.sum(m*(d_upper-b_upper+1+d_lower-b_lower+1))



