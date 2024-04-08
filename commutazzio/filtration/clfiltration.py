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
from collections import defaultdict
from orjson import dumps, OPT_SERIALIZE_NUMPY

from .simplicial_complex import SimplicialComplex
from .simplex_tree import SimplexTree
import matplotlib.pyplot as plt
from os.path import abspath
import numpy as np
from functools import cache

class CLFiltration():
    Epsilon = 1e-10 # for numerical comparison

    def __init__(self,upper=SimplexTree(),lower=SimplexTree(),ladder_length=4,h_params=None,info={},enable_validation=True,verbose=False):
        self.ladder_length=ladder_length
        if h_params is None: 
            # print(f'{self.__class__.__name__}:assuming ordinal number filtration values.')
            if not set([int(_) for _ in upper.filtration_values]).issubset(set(range(1,ladder_length+1))) or not set([int(_) for _ in lower.filtration_values]).issubset(set(range(1,ladder_length+1))):
                raise ValueError('Filtration values of the input not matching the ordinal number filtration values')
            if ladder_length < len(upper.filtration_values) or ladder_length < len(lower.filtration_values):
                raise ValueError('The ladder length is shorter than the number of filtration values in the input')
            # horizontal parameters, a list of length ladder_length, maps an index to a parameter
            self.horizontal_parameters = list(range(1,ladder_length+1))
            self.upper = upper # a SimplexTree, filtration values are 1,2,3,...,length
            self.lower = lower # a SimplexTree, filtration values are 1,2,3,...,length
        else:
            self.horizontal_parameters = h_params
            #has to be sorted
            if not all(h_params[i] <= h_params[i+1] for i in range(len(h_params) - 1)):
                raise ValueError('horizontal parameters must be sorted.')
            if not len(h_params) == ladder_length:
                raise ValueError('The length of the horizontal parameters does not match the ladder length.')
            # will not rescale again if the filtration values are already ordinal numbers
            if not set([int(_) for _ in upper.filtration_values]).issubset(set(range(1,ladder_length+1))) or not set([int(_) for _ in lower.filtration_values]).issubset(set(range(1,ladder_length+1))):
                if verbose:
                    print(f'{self.__class__.__name__}:rescaling filtration values to ordinal numbers.')
                self.upper = upper.to_ordinal_number_indexing(h_params) # a SimplexTree, filtration values are 1,2,3,...,length
                self.lower = lower.to_ordinal_number_indexing(h_params) # a SimplexTree, filtration values are 1,2,3,...,length
            else:
                if verbose:
                    print(f'{self.__class__.__name__}:ordinal number filtration values detected, will not rescale.')
                self.upper = upper
                self.lower = lower
        # for example, it can be a list of radii 
        self.info = dict(**info)
        if enable_validation:
            # automatic validation
            if not self.validation():
                raise ValueError('The input is not a valid commutative ladder filtration.')


    def get_filtration_fv(self,layer:str):
        return self.get_filtration_with_custom_filtration_values(layer)
    
    @cache
    def get_filtration_with_custom_filtration_values(self,layer:str):
        """
        return the filtration with original filtration values by layer
        """
        if layer in ['u','upper']:
            filtration = self.upper.to_custom_filtration_values(self.horizontal_parameters)
        elif layer in ['l','lower']:
            filtration =  self.lower.to_custom_filtration_values(self.horizontal_parameters)
        else:
            raise ValueError('layer must be either upper or lower')
        return filtration



    @property
    def h_params(self):
        return self.horizontal_parameters
    
    def set_info(self,info:dict):
        # make sure that the stored format is json-serializable
        self.info = info
    
    def info_update(self,kv_dict):
        self.info.update(kv_dict)

    def info_key_append(self,key,value):
        if key not in self.info:
            self.info[key] = []
        self.info[key].append(value)

    def resample_filtration(self,new_length,ordinal_filtration_values=None):
        """
        This method allows the user to refactor the length of the ladder.
        new_length shall be strictly shorter than the current length.
        ordinal_filtration_values: a list of length new_length consisting of integers between 1 and the current ladder length.
        new_h_params will be set to a random choice on [1,2,3,...,new_length] if not given.
        """
        if new_length >= self.ladder_length:
            raise ValueError("new_length must be strictly shorter than the current length")
        if ordinal_filtration_values is None: 
            # will be a strictly increasing list of length new_length, picking values from 1,...,self.ladder_length
            indices = np.random.choice(range(1,self.ladder_length+1), new_length,replace=False)
        else:
            indices = ordinal_filtration_values
        for i in indices:
            # i has to be an integer, or 1.0
            if not isinstance(i,int):
                raise ValueError("Each element in ordinal_filtration_values must be an integer")
            if not 1 <= i <= self.ladder_length:
                raise ValueError("Each element in ordinal_filtration_values must be between 1 and the current ladder length")
        if len(indices) != new_length:
            raise ValueError(f"indices must be a list of length {new_length}")
        if len(set(indices)) != new_length:
            raise ValueError("indices must be a list of distinct integers")

        new_upper = SimplexTree()
        new_lower = SimplexTree()
        # Reassign filtration values
        for simplex, original_ordinal_fv in self.upper.get_filtration():
            # new filtration value is determined by its relative position in indices
            # for example, if indices = [2,4,6], then the filtration value of a simplex with original filtration value 4 is 2
            # and the new filtration value of a simplex with original filtration value 3 is also 2,
            # and the new filtration value of simplex with original filtration value 2 is 1
            for new_ordinal_fv,current_ordinal_fv in enumerate(indices):
                if  original_ordinal_fv <= current_ordinal_fv:
                    new_upper.insert(simplex,new_ordinal_fv+1) #one-based
                    break
            else:
                pass # will not add the simplex to the new filtration            
        for simplex, original_ordinal_fv in self.lower.get_filtration():
            for new_ordinal_fv,current_ordinal_fv in enumerate(indices):
                if  original_ordinal_fv <= current_ordinal_fv:
                    new_lower.insert(simplex,new_ordinal_fv+1) #one-based
                    break
            else:
                pass # will not add the simplex to the new filtration   
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
    
    # @cache
    def get_simplicial_complex(self,x:int,y:int):
        """
        return the simplicial complex of the given coordinate (x,y)
        x: an ordinal number, 1,2,...,ladder_length
        """
        if y == 2:
            filtration = self.upper.get_filtration()
        elif y == 1:
            filtration = self.lower.get_filtration()
        else:
            raise ValueError('The y-coordinate must be either 1 or 2')
        if x > self.ladder_length and x!=float('inf'): #if x is larger than the ladder length, raise a warning
            warn('The x-coordinate is larger than the largest filtration value')
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
        # modify upper and lower such that all faces are included
        upper_dict = defaultdict(list)
        lower_dict = defaultdict(list)
        for s,fv in upper:
            upper_dict[fv].append(s)
        for s,fv in lower:
            lower_dict[fv].append(s)
        # sort the simplices in each list, first by length, then by lexicographic order
        for i in range(1,self.ladder_length+1):
            if i in upper_dict.keys():
                upper_dict[i] = self._sort(upper_dict[i])
            if i in lower_dict.keys():
                lower_dict[i] = self._sort(lower_dict[i])
        output = ["# dim birth n m v_0 .. v_dim (CECH_RANDOM)"]
        for i in range(1,self.ladder_length+1):
            col_seen = set() # do not add simplex added in the lower layer to the upper layer again
            if i in lower_dict.keys():
                for s in sorted(lower_dict[i],key=lambda x: len(x)):
                    output.append(f'{len(s)-1} {self.horizontal_parameters[i-1]} 0 {i-1} {" ".join(map(str,s))}')
                    col_seen.add(s)
            if i in upper_dict.keys():
                for s in sorted(upper_dict[i],key=lambda x: len(x)):
                    if s not in col_seen:
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
                'horizontal_parameters':dumps(self.horizontal_parameters,option=OPT_SERIALIZE_NUMPY),
                'info':dumps(self.info, option=OPT_SERIALIZE_NUMPY)}

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
    def __init__(self, *args):
        # Check if the input arguments are SimplicialComplex objects
        if isinstance(args[0],SimplicialComplex):
            pass
        elif isinstance(args[0],list):
            pass
        else: 
            raise NotImplementedError('Each variable must be a simplicial complex object or a list')
        
        # Initialize the ensemble as an empty set and times as an empty dictionary
        self.ensemble = set()
        self.times = {}
        # Initialize a dictionary to keep track of the last known presence status of each simplex
        last_presence = {}

        # Iterate over the SimplicialComplex objects in args
        for i, simplicial_complex in enumerate(args):
            # Initialize a dictionary to keep track of the current presence status of each simplex
            current_presence = {simplex: False for simplex in self.ensemble}
            if isinstance(simplicial_complex,SimplicialComplex):
                simplicial_complex = simplicial_complex.simplices
            # Iterate over the simplices in the current SimplicialComplex object
            for simplex in simplicial_complex:
                # If the simplex is not in the ensemble, add it and initialize its times and last presence status
                if simplex not in self.ensemble:
                    self.ensemble.add(simplex)
                    self.times[simplex] = []
                    last_presence[simplex] = False
                # Set the current presence status of the simplex to True
                current_presence[simplex] = True

            # Check for simplices in the ensemble whose presence status has changed
            # If a simplex's presence status has changed, append the current time to its times
            # and update its last presence status
            for simplex in self.ensemble:
                if last_presence[simplex] != current_presence[simplex]:
                    self.times[simplex].append(i)
                    last_presence[simplex] = current_presence[simplex]

        # Convert the ensemble to a sorted list and times to a list of lists
        self.ensemble = sorted(list(self.ensemble))
        self.times = [self.times[simplex] for simplex in self.ensemble]

    # Method to return the times
    def all_time_sequences(self):
        return self.times





# class ZigzagFiltration:
#     def __init__(self,*args):
#         """Input: each variable is a simplicial complex.
#         """
#         # if type(args[0]).__name__ != 'SimplicialComplex':
#         #     raise NotImplementedError('Each variable must be a simplicial complex object')
#         # self.ensemble=[]
#         # #if type(args[0][0][0]) is list and len(args)==1:
#         # #    args=tuple(args[0]) # dealing with the case when the input is not spread
#         # self.sequence=[simplicial_complex_object.simplices for simplicial_complex_object in args]
#         # for simplicial_complex_list in self.sequence:
#         #     for simplex in simplicial_complex_list:
#         #         if simplex not in self.ensemble:
#         #             self.ensemble.append(simplex)
#         # self.ensemble.sort()

#         if type(args[0]).__name__ != 'SimplicialComplex':
#             raise NotImplementedError('Each variable must be a simplicial complex object')
#         #args: simplicial complexes in order, in an alternating orientation
#         self.sequence = [_.simplices for _ in args] 
#         self.ensemble = set() # the set of all simplices
#         for simplicial_complex_list in self.sequence:
#             self.ensemble |= set(simplicial_complex_list)
#         self.ensemble = list(self.ensemble)
#         self.ensemble.sort()
    
#     def time_sequence(self,simplex):
#         """Register the attendence-absence vector of a simplex"""
#         state = 0
#         seq=[]
#         for i,item in enumerate(self.sequence):
#             if simplex in item:
#                 new_state = 1
#             else:
#                 new_state = 0
#             if new_state != state:
#                 seq.append(i)
#             else:
#                 pass
#             state=new_state
#         return seq
            
#     def all_time_sequences(self):
#         """Find the time vectors for all simplices"""
#         if hasattr(self, 'times'):
#             return self.times
#         else:
#             self.times = [self.time_sequence(simplex) for simplex in self.ensemble]
#             return self.times
            # self.times=[]
            # for simplex in self.ensemble:
            #     self.times.append(self.time_sequence(simplex))
            # return self.times

        
    
    
    
    
