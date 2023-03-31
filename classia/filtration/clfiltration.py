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
from gudhi import SimplexTree

class CLFiltration():
    def __init__(self,length=4):
        self.upper = SimplexTree()
        self.lower = SimplexTree()
        self.ladder_length=length
        self.metadata = {}

    def __repr__(self) -> str:
        """
        returns both the upper and lower rows
        """
        return f'Upper row: {list(self.upper.get_filtration())}, \
                    Lower row: {list(self.lower.get_filtration())}'


    def from_database_item(self, item):
        #add a verification function somewhere else
        self.ladder_length = item['ladder_length']
        self.upper = self.incremental_filtration_creation(item['upper'])
        self.lower = self.incremental_filtration_creation(item['lower'])
        self.metadata = item['metadata']
    
    def incremental_filtration_creation(self,increments:list):
        """
        Create the filtration by adding simplices one by one.
        """
        filtration=SimplexTree()
        for i,increment in enumerate(increments):
            for simplex in increment:
                filtration.insert(simplex,i)
        return filtration
    
    def serialize(self):
        """
        Convert the filtration to a dictionary.
        """
        return {'ladder_length':self.ladder_length,
                'upper':self.upper.get_filtration(),
                'lower':self.lower.get_filtration(),
                'metadata':self.metadata}

    def verify(self):
        """
        Verify that the two rows are indeed simplicial complexes,
        and the lower row is contained in the upper row for each filtration value
        """
        ...

    def visualisation(self):
        """
        Visualise the filtration, using networkx?
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
    
    
    
    
