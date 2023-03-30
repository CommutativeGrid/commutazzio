#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 28 22:01:47 2021

@author: kasumi
"""
#import dionysus as d
from warnings import warn
from functools import cache
import numpy as np

from .simplicial_complex import SimplicialComplex

class CLFiltration():
    def __init__(self,length=4):
        X_n2 = SimplicialComplex()
        X_n1 = SimplicialComplex()
        self.ladder_length=length
        self.diff_list_upper=[]
        self.diff_list_lower=[]

    @cache
    def X(self,x,y):
        """
        Return the simplicial complex at coordinate (x,y).
        """
        if x==n:
            if y==2:
                return self.X_n2
            elif y==1:
                return self.X_n1
            else:
                raise ValueError(f'y={y} is out of range')
            
        if y == 2:
            X_temp = self.X_n2
            for i,to_be_removed in reversed(enumerate(self.diff_list_upper)):
                X_temp = X_temp.delete_simplices(to_be_removed)
                if i+1 == x:
                    break
        elif y == 1:
            X_temp = self.X_n1
            for i,to_be_removed in reversed(enumerate(self.diff_list_lower)):
                X_temp = X_temp.delete_simplices(to_be_removed)
                if i+1 == x:
                    break
        else:
            raise ValueError(f'y={y} is out of range')
        return X_temp

    def visualisation(self):
        """
        Visualise the filtration.
        """
        ...

        
    def verify(self):
        """
        Verify that the two rows are indeed simplicial complexes,
        and the lower row is contained in the upper row.
        """
        ...
    

    



class ZigzagFiltration:
    def __init__(self,*args):
        """Input: each variable is a simplicial complex.
        """
        self.ensemble=[]
        if type(args[0]).__name__ != 'SimplicialComplex':
            raise NotImplementedError('Each variable must be a simplicial complex object')
        #if type(args[0][0][0]) is list and len(args)==1:
        #    args=tuple(args[0]) # dealing with the case when the input is not spread
        self.sequence=[simplicial_complex_object.sc for simplicial_complex_object in args]
        for simplicial_complex_list in self.sequence:
            for simplex in simplicial_complex_list:
                if simplex not in self.ensemble:
                    self.ensemble.append(simplex)
        self.ensemble.sort()
    
    def time_sequence(self,simplex):
        """Register the attendence-absence vector of a simplex"""
        state = 0
        seq=[]
        for i,item in enumerate(self.sequence):
            if simplex in item:
                new_state = 1
            else:
                new_state = 0
            if new_state != state:
                seq.append(i)
            else:
                pass
            state=new_state
        return seq
            
    def all_time_sequences(self):
        """Find the time vectors for all simplices"""
        if hasattr(self, 'times'):
            breakpoint()
            return self.times
        else:        
            self.times=[]
            for simplex in self.ensemble:
                self.times.append(self.time_sequence(simplex))
            return self.times
        
        

# if __name__ == '__main__':
#     example=([[1]],# the first sc
#                        [[0],[1]], # the second sc
#                        [[1]],
#                        [[0],[1]],
#                        [[0],[1],[2],[0,1],[0,2],[1,2]])
                       
#     a=ZigzagFiltration(*example)
    
#     f=d.Filtration(a.ensemble)
#     times=a.all_time_sequences()
    
#     zz, dgms, cells = d.zigzag_homology_persistence(f, times)
#     print(zz)
#     for i,dgm in enumerate(dgms):
#         print("Dimension:", i)
#         for p in dgm:
#             print(p)
    
    
    
    
