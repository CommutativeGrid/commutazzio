#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 16:21:47 2021

@author: kasumi
"""
import dionysus as d
import numpy as np
from gudhi import SimplexTree as gudhi_SimplexTree
from itertools import combinations
import dionysus as d

    
class SimplicialComplex(gudhi_SimplexTree):
    def __init__(self):
        # cannot override __cinit__ in Cython
        # it is called even before __init__
        # https://stackoverflow.com/questions/18260095/cant-override-init-of-class-from-cython-extension
        super().__init__()
        
    def from_simplices(self, simplices):
        if len(simplices) == 0:
            return SimplicialComplex()
        if isinstance(simplices, list) and len(simplices) > 0: # if the input is not empty, verify whether the form complies with the standard
            if not isinstance(simplices[0], (tuple, set, frozenset)):
                raise ValueError('Each simplex should be represented by a tuple, set or frozenset.')
            for simplex in simplices:
                self.insert(list(simplex))
        else:
            raise TypeError('Invalid input type. Must be a SimplexTree or list of tuples.')
        
    def betti_numbers(self):
        # use dionysus to compute betti numbers
        filtration = d.Filtration([d.Simplex(s) for s in self.simplices])
        homology = d.homology_persistence(filtration)
        dgms = d.init_diagrams(homology, filtration)
        # Compute the Betti numbers
        betti_numbers = [len(dgm) for dgm in dgms]
        # Remove trailing zeros
        while len(betti_numbers)>1 and betti_numbers[-1] == 0:
            betti_numbers.pop()
        return betti_numbers
    
    
    @property
    def simplices(self):
        ss=[_[0] for _ in list(self.get_simplices())]
        ss.sort(key=lambda x: (len(x),tuple(x)))
        return [tuple(_) for _ in ss]
    
    @property
    def sc(self):
        return self.simplices
    
    def __iter__(self):
        return self.simplices
    
    @simplices.setter
    def simplices(self, value):
        self.from_simplices(value)
    
    def __str__(self):
        sf_pairs=list(self.get_filtration())
        first_filtration_value = sf_pairs[0][1]
        last_filtration_value = sf_pairs[-1][1]
        if first_filtration_value != last_filtration_value:
            raise ValueError('Filtration should be a list of length 1.')
        return str(self.simplices)

    def __repr__(self):
        description = (f"a simplicial complex with "
                       f"{len(list(self.get_simplices()))} simplices "
                       f"@ {hex(id(self))}"
            )
        return description
    
    def __eq__(self, other):
        return self.simplices == other.simplices
    
    def __len__(self):
        return len(self.simplices)

    
    def dionysus_form(self):
        return [list(s) for s in self.simplices]
    
    def info_node(self):
        return {'simplicial_complex':self,'num_simplices':len(self.simplices)}
    
    def issimplicialComplex(self):
        ...

    def is_subcomplex_of(self,external_sc):
        if type(external_sc).__name__ == 'list':
            return set(self.simplices).issubset(external_sc)
        elif type(external_sc).__name__ == 'SimplicialComplex':
            return set(self.simplices).issubset(external_sc.simplices)
        
    def issuperset(self,external_sc):
        if type(external_sc).__name__ == 'list':
            return set(external_sc).issubset(set(self.sc))
        elif type(external_sc).__name__ == 'SimplicialComplex':
            return set(external_sc.sc).issubset(set(self.sc))
        
    
    @staticmethod
    def simplexify(simplex):
        """Normalize the representation of a simplex"""
        if type(simplex) in [int,np.int64]:
            simplex=(simplex,)
        elif type(simplex) in [tuple,list]:
            pass
        else:
            raise NotImplementedError
        return simplex


    def removeOne(self,simplex):
        """Delete one simplex, together with its superset"""
        simplex=self.simplexify(simplex)    
        new_sc=[s for s in self.sc if not set(simplex).issubset(set(s))]
        temp = SimplicialComplex()
        temp.from_simplices(new_sc)
        return temp
    
    def deleteOne(self,simplex):
        return self.removeOne(simplex)
        
    def __remove_from(self,simplex,from_sc):
        """Delete one simplex, together with its superset"""
        """seems to be very time consuming"""
        simplex=self.simplexify(simplex)    
        new_sc=[s for s in from_sc if not set(simplex).issubset(set(s))]
        return new_sc
    
    def __delete_from(self,simplex,from_sc):
        return self.__remove_from(simplex,from_sc)

    def remove_simplices(self,simplices):
        """Delete vertices"""
        intermediate_agent=self.simplices
        for simplex in simplices:
            intermediate_agent=self.__delete_from(simplex,intermediate_agent)
        temp = SimplicialComplex()
        temp.from_simplices(intermediate_agent)
        return temp
    
    def delete_simplices(self,simplices):
        # another name for remove_simplices
        return self.remove_simplices(simplices)
                        
    def add(self,simplex,inplace=False):
        """Add a simplex, together with all of its faces"""
        simplex=self.simplexify(simplex)
        all_faces_dionysus=d.closure([d.Simplex(simplex)],len(simplex)-1)
        all_faces=[tuple(s) for s in all_faces_dionysus]
        with_duplicates = self.sc+all_faces
        new_sc=list(set(with_duplicates))
        #new_sc=[]
        #for s in with_duplicates:
        #    if s not in new_sc:
        #        new_sc.append(s)
        if inplace:
            self.sc=new_sc
        else:
            return new_sc
    
    def random_delete_vertices(self,num=None,inplace=False):
        diff_low=5
        diff_high=10
        if num is None:
            num=np.random.randint(diff_low,diff_high+1) #np.random.randint is exclusive of the upper bound
        to_be_deleted=np.random.choice(self.vertices(),num,replace=False)
        new_sc=self.delete_simplices(to_be_deleted,inplace)
        return new_sc
        
    @property
    def vertices(self):
        """Returns the list of 0-simplices (vertices)."""
        # raw=[s for s in self.sc if len(s)==1]
        # return list(np.array(raw).flatten())
        return {s[0] for s in self.sc if len(s) == 1}

        
    def dimension(self):
        """Return the dimension of the simplicial complex"""
        return max([len(s) for s in self.simplices])
    

    @property
    def maximum_simplices(self):
        """
        Returns a list of maximum simplices in the simplicial complex.
        A maximum simplex is not a proper face of any other simplex in the complex.
        """
        # Group simplices by their dimension
        simplices_by_dim = {}
        for simplex in self.simplices:
            dim = len(simplex) - 1  # Dimension is one less than the length of the simplex
            if dim not in simplices_by_dim:
                simplices_by_dim[dim] = set()
            simplices_by_dim[dim].add(simplex)

        # Sort dimensions in descending order
        sorted_dims = sorted(simplices_by_dim.keys(), reverse=True)
        max_simplices = set()

        # Iterate from higher to lower dimensions
        for dim in sorted_dims:
            current_simplices = simplices_by_dim[dim]
            for simplex in current_simplices:
                max_simplices.add(simplex)
                # Remove all faces of the current simplex from consideration in lower dimensions
                for d in range(dim - 1, -1, -1):
                    faces = self.get_faces(simplex, d)
                    simplices_by_dim[d] -= set(faces)

        return list(max_simplices)

    def get_faces(self, simplex, dim):
        """
        Generate all faces of a given simplex of a specific dimension.
        """
        if dim < 0 or dim >= len(simplex):
            return []
        return [tuple(sorted(face)) for face in combinations(simplex, dim + 1)]

        
    
# if __name__ == "__main__":
#     aa=SimplicialComplex()
#     aa.from_random_point_cloud(method='cech')
    #a9=aa
    #a7=aa.random_delete_vertices()
    #a3=aa.random_delete_vertices()
    