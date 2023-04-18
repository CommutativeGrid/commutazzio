#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 28 22:01:47 2021

@author: kasumi
"""
#import dionysus as d
from warnings import warn
from functools import cache
import networkx as nx
from ..utils import filepath_generator
from random import sample

from .simplicial_complex import SimplicialComplex
from .simplex_tree import SimplexTree
import matplotlib.pyplot as plt
from os.path import abspath

class CLFiltration():
    Epsilon = 1e-6 # for numerical comparison

    def __init__(self,upper=SimplexTree(),lower=SimplexTree(),length=4,h_params=None,info={}):
        self.upper = upper # a SimplexTree, filtration values are 1,2,3,...,length
        self.lower = lower # a SimplexTree, filtration values are 1,2,3,...,length
        self.ladder_length=length
        if h_params is None: 
            # horizontal parameters, a list of length ladder_length, maps an index to a parameter
            self.horizontal_parameters = list(range(1,length+1))
        else:
            self.horizontal_parameters = h_params
        # for example, it can be a list of radii 
        self.info = dict(**info)

    @property
    def h_params(self):
        return self.horizontal_parameters
    
    def set_info(self,info):
        self.info = info
    
    def info_update(self,kv_dict):
        self.info.update(kv_dict)

    def info_key_append(self,key,value):
        if key not in self.info:
            self.info[key] = []
        self.info[key].append(value)

    def set_new_length(self,new_length,indices=None):
        """
        This method allows the user to refactor the length of the ladder.
        new_length shall be strictly shorter than the current length.
        indices will be randomized to be a list of length new_length
        if not given.
        """
        if new_length >= self.ladder_length:
            raise ValueError("new_length must be strictly shorter than the current length")
        if indices is None: 
            # will be a strictly increasing list of length new_length, picking values from 1,...,self.ladder_length
            indices = sorted(sample(range(1,self.ladder_length+1),new_length))
    
        if len(indices) != new_length:
            raise ValueError("indices must be a list of length new_length")
        if len(set(indices)) != new_length:
            raise ValueError("indices must be a list of distinct integers")
        if max(indices) > self.ladder_length:
            raise ValueError("indices must be a list of integers between 1 and the current ladder length")

        new_upper = SimplexTree(self.upper)
        new_lower = SimplexTree(self.lower)
        # Reassign filtration values
        for simplex, original_fv in self.upper.get_simplices():
            # new filtration value is determined by its relative position in indices
            # for example, if indices = [2,4,6], then the filtration value of a simplex with original filtration value 4 is 2
            # and the new filtration value of a simplex with original filtration value 3 is also 2,
            # and the new filtration value of simplex with original filtration value 2 is 1
            new_fv = len(indices)
            for i in range(len(indices)):
                if original_fv <= indices[i]:
                    new_fv = i+1
                    break
            new_upper.assign_filtration(simplex,new_fv)
        for simplex, original_fv in self.lower.get_simplices():
            new_fv = len(indices)
            for i in range(len(indices)):
                if original_fv <= indices[i]:
                    new_fv = i+1
                    break
            new_lower.assign_filtration(simplex,new_fv)
        if new_upper.make_filtration_non_decreasing() or new_lower.make_filtration_non_decreasing():
            raise ValueError("There is a bug in the code, please report it to the developer")
        # return a new CLFiltration object
        new_horizontal_parameters = [self.horizontal_parameters[i-1] for i in indices]
        new_info = dict(**self.info)
        new_info.update(ladder_length_refactored=dict(old_length=self.ladder_length,new_length=new_length,indices=indices))
        return CLFiltration(new_upper,new_lower,new_length,new_horizontal_parameters,new_info)

    
    def __len__(self):
        return self.ladder_length
    
    def __repr__(self) -> str:
        """
        returns both the upper and lower rows,
        filtration values to integers
        """
        return f'CL({self.ladder_length}) filtration {object.__repr__(self)}\n'

    
    def __str__(self) -> str:
        """
        returns both the upper and lower rows,
        filtration values to integers
        """
        upper = list(self.upper.get_filtration())
        upper = [(tuple(s), int(fv)) for s,fv in upper]
        lower = list(self.lower.get_filtration())
        lower = [(tuple(s), int(fv)) for s,fv in lower]
        return f'Upper row:\n{str(upper)},\nLower row:\n{str(lower)}'
    
    @cache
    def get_simplicial_complex(self,x:int,y:int):
        """
        return the simplicial complex of the given coordinate (x,y)
        """
        if y == 2:
            filtration = self.upper.get_filtration()
        elif y == 1:
            filtration = self.lower.get_filtration()
        else:
            raise ValueError('The y-coordinate must be either 1 or 2')
        if x>self.ladder_length and x!=float('inf'): #if x is larger than the ladder length, raise a warning
            warn('The x-coordinate is larger than the ladder length')

        # return all simplicies in filtration up to (inclusive) x
        sc=SimplicialComplex()
        sc.from_simplices([tuple(s) for s,fv in filtration if fv <= x+CLFiltration.Epsilon])
        return sc
    
    
    @staticmethod
    def _sort(nested_list):
        return sorted(nested_list,key=lambda x: (len(x),tuple(x)))
    
    
    def num_simplices(self):
        pass


    def random_cech_format_output_list(self):
        """print the filtration in the format as described in 
        https://bitbucket.org/tda-homcloud/random-cech/src/master/
        # dim birth n m v_0 .. v_dim (CECH_RANDOM)
        * 1番目のカラム: 単体の次元 
        * 2番目のカラム: その単体の発生時刻(h_params) 
        * 3番目のカラム: n 0 or 1, corresponding to 1(lower) or 2(upper) here
        * 4番目のカラム: 0...ladder_length-1, corresponding to the index of the filtration value subtracted by 1
        * 5番目以降のカラム: 頂点のインデックス，(dim + 1)個
        ordered by birth time (h_params)
        -----------------------------------
        add the lines from left to right, lower then upper.
        for each fixed m,
        if a simplex is seen in the lower row first,
        do not need to add it from the upper row
        """
        # create a dict from .get_filtration()
        # key: filtration value
        # value: list of simplices
        upper = [(tuple(s), round(fv)) for s,fv in self.upper.get_filtration()]
        lower = [(tuple(s), round(fv)) for s,fv in self.lower.get_filtration()]
        upper_dict = {}
        lower_dict = {}
        for s,fv in upper:
            if fv not in upper_dict:
                upper_dict[fv] = [s]
            else:
                upper_dict[fv].append(s)
        for s,fv in lower:
            if fv not in lower_dict:
                lower_dict[fv] = [s]
            else:
                lower_dict[fv].append(s)
        output = ["# dim birth n m v_0 .. v_dim (CECH_RANDOM)"]
        for i in range(1,self.ladder_length+1):
            seen = set()
            if i in lower_dict.keys():
                for s in sorted(lower_dict[i],key=lambda x: len(x)):
                    output.append(f'{len(s)-1} {self.horizontal_parameters[i-1]} 0 {i-1} {" ".join(map(str,s))}')
                    seen.add(s)
            if i in upper_dict.keys():
                for s in sorted(upper_dict[i],key=lambda x: len(x)):
                    if s not in seen:
                        output.append(f'{len(s)-1} {self.horizontal_parameters[i-1]} 1 {i-1} {" ".join(map(str,s))}')
        return output
    
    def random_cech_format_output_file(self,new_file=True,**kwargs):
        if new_file:
            # kwargs:
            # def filepath_generator(dirname='./',filename=None,suffix=None,overwrite=False):
            filepath = filepath_generator(**kwargs)
        else:
            filepath = kwargs['filepath']
        with open(filepath,'w') as f:
            for line in self.random_cech_format_output_list():
                f.write(f'{line}\n')
        # return the absolute path of the file
        return abspath(filepath)



    def dimension(self):
        """return both dimensions  of the final simplicial complexes"""
        return {'upper':self.upper.dimension(),'lower':self.lower.dimension()}

    def from_database_item(self, item):
        #add a verification function somewhere else
        self.ladder_length = item['ladder_length']
        self.upper = self.incremental_filtration_creation(item['upper'])
        self.lower = self.incremental_filtration_creation(item['lower'])
        self.info = item['info']

    def get_filtration_as_a_nested_list(self,layer):
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

    
    def incremental_filtration_creation(self,increments:list):
        """
        Create the filtration by adding simplices one by one.
        increments: a list of lists of simplices,
        can be the output of get_filtration_as_a_nested_list()
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
                'upper':self.get_filtration_as_a_nested_list(layer='upper'),
                'lower':self.get_filtration_as_a_nested_list(layer='lower'),
                'horizontal_parameters':self.horizontal_parameters,
                'info':self.info}

    def validation(self):
        """
        Verify that the lower row is contained in the upper row for each filtration value
        """
        for i in range(1,self.ladder_length+1):
            upper = self.get_simplicial_complex(*(i,2))
            lower = self.get_simplicial_complex(*(i,1))
            if not lower.is_subcomplex_of(upper):
                raise ValueError(f'Lower row is not a subcomplex of the upper row at filtration value {i}')
        return True

    

    def plot(self):
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
            node_labels[(x, 2)] = str(len(self.get_simplicial_complex(*(x,2))))
            node_labels[(x, 1)] = str(len(self.get_simplicial_complex(*(x,1))))

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
        self.sequence=[simplicial_complex_object.simplices for simplicial_complex_object in args]
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
    
    
    
    
