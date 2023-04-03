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
import networkx as nx

from .simplicial_complex import SimplicialComplex
from gudhi import SimplexTree
import matplotlib.pyplot as plt

class CLFiltration():
    Epsilon = 1e-6 # for numerical comparison

    def __init__(self,length=4):
        self.upper = SimplexTree()
        self.lower = SimplexTree()
        self.ladder_length=length
        self.horizontal_parameters = list(range(1,length+1)) # horizontal parameters, a list of length ladder_length,
        # for example, it can be a list of radii 
        self.metadata = {}

    @property
    def h_params(self):
        return self.horizontal_parameters
    
    def __repr__(self) -> str:
        """
        returns both the upper and lower rows
        """
        return f'Upper row: {list(self.upper.get_filtration())}, \
                    Lower row: {list(self.lower.get_filtration())}'
    

    def get_simplicial_complex(self, coordinate:tuple[int,int]):
        """
        return the simplicial complex of the given coordinate (x,y)
        """
        x,y = coordinate
        if y == 2:
            filtration = self.upper.get_filtration()
        elif y == 1:
            filtration = self.lower.get_filtration()
        else:
            raise ValueError('The y-coordinate must be either 1 or 2')
        # return all simplicies in filtration up to (inclusive) x
        sc=SimplicialComplex()
        sc.from_simplices([tuple(s) for s,fv in filtration if fv <= x+CLFiltration.Epsilon])
        return sc
    
    @staticmethod
    def _sort(nested_list):
        return sorted(nested_list,key=lambda x: (len(x),tuple(x)))
    
    def get_filtration_as_nested_list(self,layer='upper'):
        """
        return the filtration as a nested list
        """
        if layer in ['u','upper']:
            filtration = list(self.upper.get_filtration())
        elif layer in ['l','lower']:
            filtration =  list(self.lower.get_filtration())
        else:
            raise ValueError('layer must be either upper or lower')
        return [self._sort([s for s,fv in filtration if abs(fv-i)<CLFiltration.Epsilon ]) for i in range(1,self.ladder_length+1)]
    
    def num_simplices(self):
        pass
        

    def dimension(self):
        """return both dimensions  of the final simplicial complexes"""
        return {'upper':self.upper.dimension(),'lower':self.lower.dimension()}

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
                filtration.insert(simplex,i+1)
        return filtration
    
    def serialize(self):
        """
        Convert the filtration to a dictionary.
        """
        return {'ladder_length':self.ladder_length,
                'upper':self.get_filtration_as_nested_list(layer='upper'),
                'lower':self.get_filtration_as_nested_list(layer='lower'),
                'horizontal_parameters':self.horizontal_parameters,
                'metadata':self.metadata}

    def validation(self):
        """
        Verify that the lower row is contained in the upper row for each filtration value
        """
        for i in range(1,self.ladder_length+1):
            upper = self.get_simplicial_complex((i,2))
            lower = self.get_simplicial_complex((i,1))
            if not lower.is_subcomplex_of(upper):
                raise ValueError(f'Lower row is not a subcomplex of the upper row at filtration value {i}')
        return True

    

    def visualization(self):
        """
        Visualise the filtration, using networkx
        draw a commutative ladder graph, with number of simplicial complexes on each node
        which looks like below
        *--*--*--*--*--*
        |  |  |  |  |  | 
        *--*--*--*--*--*
        """
        # Create a directed graph
        G = nx.DiGraph()

        # Add nodes for each layer and filtration value
        for x in range(1,self.ladder_length+1):
            for y in [1,2]:
                G.add_node((x, y))

        # Add horizontal edges
        for x in range(1,self.ladder_length):
            G.add_edge((x, 2), (x+1, 2), arrowstyle='->')
            G.add_edge((x, 1), (x+1, 1), arrowstyle='->')
        
        # Add vertical edges
        for x in range(1,self.ladder_length+1):
            G.add_edge((x, 1), (x, 2), arrowstyle='->')

        # Add labels to nodes
        node_labels = {}
        for x in range(1,self.ladder_length+1):
            node_labels[(x, 2)] = str(len(self.get_simplicial_complex((x+1,2))))
            node_labels[(x, 1)] = str(len(self.get_simplicial_complex((x+1,1))))

        # Draw the graph
        pos = {node: (node[0], node[1]) for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=14)
        nx.draw_networkx_nodes(G, pos, nodelist=[(i, 2) for i in range(1,self.ladder_length+1)], node_color='lightcyan', node_shape='o', node_size=500)
        nx.draw_networkx_nodes(G, pos, nodelist=[(i, 1) for i in range(1,self.ladder_length+1)], node_color='lightcyan', node_shape='o', node_size=500)
        nx.draw_networkx_edges(G, pos, arrows=True,arrowsize=20)
        plt.axis('off')
        plt.show()
        return G





        


        

    

    



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
    
    
    
    
