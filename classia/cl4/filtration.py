#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 28 22:01:47 2021

@author: kasumi
"""
#import dionysus as d
from warnings import warn
import numpy as np

from .simplicial_complex import SimplicialComplex

class CLFiltration():
    def __init__(self,pt_cloud,size=4,method='cech',sc_dim_ceil='auto',radius_max=np.inf):
        sc=SimplicialComplex()
        self.num_pts=pt_cloud.shape[0]
        self.space_dim=pt_cloud.shape[1]
        self.pt_cloud=pt_cloud
        sc.from_point_cloud(pt_cloud,method=method,sc_dim_ceil=sc_dim_ceil,radius_max=radius_max)
        self.upper_sc=sc
        self.ladder_length=size
        if len(self.upper_sc.radii_list) < self.ladder_length:
            warn('Number of critical radius values smaller than the ladder length')

    # def remove_vertices(self,to_be_removed:list):
    #     """
    #     Remove vertices and associated simplexes in the list.
    #     Generate the simplicial complex for the lower row.
    #     vertices of form [(v0),(v1),...]
    #     """
    #     self.lower_sc=self.upper_sc.delete_simplices(to_be_removed)
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
    
    def set_radii(self,radii_list):
        self.radii=radii_list

    def set_removal_list(self,removal_list):
        self.removal_list=removal_list

    @property
    def upper_row(self):
        """
        Return the filtration of the upper row.
        """
        #TODO: progressive removal of vertices
        if hasattr(self,'radii'):
            return [self.upper_sc.truncation(r) for r in self.radii]
        else:
            raise ValueError('Radii not set yet.')

    @property
    def lower_row(self):
        """
        Return the filtration of the lower row.
        """
        return [sc.delete_simplices(self.removal_list) for sc in self.upper_row]

    @property
    def radii_list(self):
        return self.upper_sc.radii_list
    

    



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
    
    
    
    
