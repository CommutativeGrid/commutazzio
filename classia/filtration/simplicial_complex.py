#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 16:21:47 2021

@author: kasumi
"""
import dionysus as d
import numpy as np
from scipy.spatial import distance
from gudhi import SimplexTree
import gudhi as gd
from gtda.externals import CechComplex
    
class SimplicialComplex(SimplexTree):
    def __init__(self):
        # cannot override __cinit__ in Cython
        # it is called even before __init__
        # https://stackoverflow.com/questions/18260095/cant-override-init-of-class-from-cython-extension
        super().__init__()
        
    def from_simplices(self, simplices):
        if isinstance(simplices, list) and len(simplices) > 0: # if the input is not empty, verify whether the form complies with the standard
            if not isinstance(simplices[0], tuple):
                raise ValueError('Each simplex should be represented by a tuple.')
            for simplex in simplices:
                print(simplex)
                self.insert(list(simplex))
        else:
            raise TypeError('Invalid input type. Must be a SimplexTree or list of tuples.')
    
    @property
    def simplices(self):
        ss=[_[0] for _ in list(self.get_simplices())]
        ss.sort(key=lambda x: (len(x),tuple(x)))
        return [tuple(_) for _ in ss]
    
    def __str__(self):
        sf_pairs=list(self.get_filtration())
        first_filtration_value = sf_pairs[0][1]
        last_filtration_value = sf_pairs[-1][1]
        if first_filtration_value != last_filtration_value:
            raise ValueError('Filtration should be a list of length 1.')
        return str(self.sc)

    def __repr__(self):
        description = f"a simplicial complex with {len(list(self.get_simplices()))} simplices"
        return description

    
    def dionysus_form(self):
        return [list(s) for s in self.simplices]
    
    def info_node(self):
        return {'sc':self,'sc_size':len(self.simplices)}

    def from_point_cloud(self,pt_cloud,method='cech',sc_dim_ceil='auto',radius_max=np.inf):
        """
        Create a simplicial complex from a point cloud.
        """
        space_dim,num_pts=pt_cloud.shape
        if sc_dim_ceil == 'auto':
            sc_dim_ceil = space_dim-1  # maximum dimension of the simplicial complex.
        if method == 'rips':
            rips_complex = gd.RipsComplex(pt_cloud,max_edge_length=radius_max)
            simplex_tree = rips_complex.create_simplex_tree(max_dimension=sc_dim_ceil)
            simplex_tree.make_filtration_non_decreasing()
            simplices_list = [tuple(s[0]) for s in simplex_tree.get_filtration()]
        elif method == 'alpha':
            alpha_complex = gd.AlphaComplex(points=pt_cloud)
            simplex_tree = alpha_complex.create_simplex_tree()
            simplex_tree.make_filtration_non_decreasing()
            simplices_list = [tuple(s[0]) for s in simplex_tree.get_filtration()]
        elif method == 'cech':
            cech_complex = CechComplex(points=pt_cloud,max_radius=np.inf)
            simplex_tree = cech_complex.create_simplex_tree(max_dimension=sc_dim_ceil)
            simplex_tree.make_filtration_non_decreasing()
            simplices_list = [tuple(s[0]) for s in simplex_tree.get_filtration()]
        elif method == 'weak-witness':
            diameter = max(distance.cdist(pt_cloud,pt_cloud,'euclidean').flatten())
            witnesses=pt_cloud
            w_l_ratio=5
            n_landmarks=int(len(pt_cloud)/w_l_ratio) # vertices consist of landmarks. A too low value may cause zero candidates available for being deleted.
            landmarks=gd.pick_n_random_points(points=pt_cloud,nb_points=n_landmarks)
            witness_complex = gd.EuclideanWitnessComplex(witnesses=witnesses, landmarks=landmarks)
            max_alpha_square = diameter/50.0
            simplex_tree = witness_complex.create_simplex_tree(max_alpha_square=max_alpha_square,limit_dimension=sc_dim_ceil)
            simplex_tree.make_filtration_non_decreasing()
            simplices_list = [tuple(s[0]) for s in simplex_tree.get_filtration()]
            print(len(simplices_list))
        elif method == 'strong-witness':
            diameter = max(distance.cdist(pt_cloud,pt_cloud,'euclidean').flatten())
            witnesses=pt_cloud
            w_l_ratio=5
            n_landmarks=int(len(pt_cloud)/w_l_ratio)
            landmarks=gd.pick_n_random_points(points=pt_cloud,nb_points=n_landmarks)
            witness_complex = gd.EuclideanStrongWitnessComplex(witnesses=witnesses, landmarks=landmarks)
            max_alpha_square = diameter/50.0
            simplex_tree = witness_complex.create_simplex_tree(max_alpha_square=max_alpha_square,limit_dimension=sc_dim_ceil)
            simplex_tree.make_filtration_non_decreasing()
            simplices_list = [tuple(s[0]) for s in simplex_tree.get_filtration()]
        else:
            raise NotImplementedError('Method not supported.')
        #filtration = d.fill_rips(points,sc_dim_ceil,radius_max) obsolete, too slow
        self.simplex_tree = simplex_tree
        self.sc=simplices_list
    
    @property
    def radii_list(self):
        return np.sort(list(set([item[1] for item in self.simplex_tree.get_filtration()])))

    def from_random_point_cloud(self,nb_pts=100,space_dim=3,sc_dim_ceil='auto',radius_max=np.inf,method='alpha'):
        """
        Generate a simplicial complex out of a random point cloud,
        using the given method.

        Parameters
        ----------
        nb_pts : 
            Number of points in the point cloud. The default is 100.
        space_dim : TYPE, optional
            Dimension of the point cloud. The default is 3.
        sc_dim_ceil : TYPE, optiona, the default is pc_dim - 1
           
        method : TYPE, optional
            Method to be used. Supported methods are 'rips', 'alpha', 'weak-witness' and 'strong-witness'.
            Using gudhi library to generate the array of simplices.
            https://geometrica.saclay.inria.fr/team/Fred.Chazal/slides/Intro_TDA_with_GUDHI_Part_1.html

        Returns
        -------
        A simplicial complex represented by a list of tuples.

        """
        pt_cloud=np.random.random([nb_pts,space_dim]) # generate a random point cloud
        self.from_point_cloud(pt_cloud,method=method,sc_dim_ceil=sc_dim_ceil,radius_max=radius_max)
    
    def issubset(self,external_sc):
        if type(external_sc).__name__ == 'list':
            return set(self.sc).issubset(external_sc)
        elif type(external_sc).__name__ == 'SimplicialComplex':
            return set(self.sc).issubset(external_sc.sc)
        
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
    
    def truncation(self,ceiling):
        return SimplicialComplex([tuple(s[0]) for s in self.simplex_tree.get_filtration() if s[1]<=ceiling])

    def deleteOne(self,simplex,inplace=False):
        """Delete one simplex, together with its superset"""
        simplex=self.simplexify(simplex)    
        new_sc=[s for s in self.sc if not set(simplex).issubset(set(s))]
        if inplace:
            self.sc=new_sc
        else:
            return SimplicialComplex(new_sc)
        
    def __delete_from(self,simplex,from_sc):
        """Delete one simplex, together with its superset"""
        simplex=self.simplexify(simplex)    
        new_sc=[s for s in from_sc if not set(simplex).issubset(set(s))]
        return new_sc

    def delete_simplices(self,simplices,inplace=False):
        """Delete vertices"""
        intermediate_agent=self.sc
        for simplex in simplices:
            intermediate_agent=self.__delete_from(simplex,intermediate_agent)
        if inplace:
            self.sc=intermediate_agent
        else:
            return SimplicialComplex(intermediate_agent)
                        
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
            num=np.random.randint(diff_low,diff_high)
        to_be_deleted=np.random.choice(self.vertices(),num,replace=False)
        new_sc=self.delete_simplices(to_be_deleted,inplace)
        return new_sc
        
        
    def vertices(self):
        """Returns the list of 0-simplices (vertices)."""
        raw=[s for s in self.sc if len(s)==1]
        return list(np.array(raw).flatten())

        
    def dimension(self):
        """Return the dimension of the simplicial complex"""
        return max([len(s) for s in self.sc])
        
        
    
# if __name__ == "__main__":
#     aa=SimplicialComplex()
#     aa.from_random_point_cloud(method='cech')
    #a9=aa
    #a7=aa.random_delete_vertices()
    #a3=aa.random_delete_vertices()
    