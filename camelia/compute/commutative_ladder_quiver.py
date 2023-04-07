#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 31 19:20:11 2021

@author: kasumi
"""

import networkx as nx
import numpy as np
from .commutative_grid_quiver import CommutativeGrid2DQuiver
# from ..filtration import SimplicialComplex
from .tours import tours_cl3,tours_cl4,coeff_mat
from .decomposition_container import DecompositionCollection
from ..utils import timeit
from pathos.multiprocessing import ProcessingPool as Pool
from collections import OrderedDict
from cpes import *
# import gudhi as gd
# from gtda.externals import CechComplex

cl4_equi_isoclasses=[f"N{i}" for i in range(1,22)]+[f"I{i}" for i in range(1,56)]


class CommutativeLadderQuiver(CommutativeGrid2DQuiver):
    """
    Equi-oriented by default
    """
    def __init__(self,m:int,orientation:str='equi',one_based=True):
        super().__init__(m,2,orientation=orientation,one_based=one_based)
        if orientation in ['equi','ff','fff']: # Specify the tours for the two cases below
            if m==3:
                self.tours_list=tours_cl3(one_based=one_based)
            elif m==4:
                self.tours_list=tours_cl4(one_based=one_based)
                self.coeff_mat=coeff_mat
        self.decomp_collection=DecompositionCollection()
        self.tours=OrderedDict((f"t_{i+1}",tour) for (i,tour) in enumerate(self.tours_list))
        del(self.tours_list)



    #TODO:move to another class
    def filtration_input(self,upper_row,lower_row):
        """
        """
        horizontal_counter = range(0,self.shape[0])
        #vertical_counter = range(self.offset,self.shape[1]+self.offset)
        for i in horizontal_counter:
            values = {
                (i+self.offset,1+self.offset):upper_row[i].info_node(), #fill nodes in the upper row
                (i+self.offset,0+self.offset):lower_row[i].info_node() #fill nodes in the lower row
            }
            nx.set_node_attributes(self.G, values=values)
        # self.plot() 
        print("Filtration updated.")


    def multiplicity_zigzag_pool(self,args):
        """
        Compute the multiplicity of a zigzag tour
        """
        return self.multiplicity_zigzag(*args)
    
    #@timeit
    def tours_vector(self,dim=1,prime=2,mp_method=0):
        """
        Returns the vector of all the tours over the simplicial complex.
        mp_method: multiprocessing method, 0 for none, 1 for pool
        """
        m=self.shape[0]
        if set(self.orientation)!={'f'} or (m!=3 and m!=4):
            raise NotImplementedError("Incompatible orientation.")
        # parallel computing here
        if mp_method == 0:
            vector_list=[[self.multiplicity_zigzag(tour,dim,prime)] for tour in self.tours.values()]
        elif mp_method == 1:
            params=[(tour,dim,prime) for tour in self.tours.values()]
            with Pool() as pool: # the same as Pool(os.cpu_count())
                results=pool.map(self.multiplicity_zigzag_pool,params)
                vector_list = [[result] for result in results]
            #breakpoint()
        else:
            raise NotImplementedError("Incompatible mp_method.")
        vector=np.array(vector_list)
        return vector.astype(int)

        

    def multiplicity_computation(self,dim=1,prime=2,recalculate=False,mp_method=0,output_message=True):
        """Return the vector of multiplicities"""
        if mp_method == 1:
            raise NotImplementedError("Multiprocessing computation not implemented yet.")
        
        if len(self.decomp_collection.dim(dim).prime(prime).collection)!=0 and not recalculate:
            print("Already existed. Pass parameter recalculate=True to recalculate.")
        else:
            b=self.tours_vector(dim=dim,prime=prime,mp_method=mp_method)
            result=np.linalg.solve(self.coeff_mat,b)
            rounded=result.round().astype(int)
            error=np.linalg.norm(np.matmul(self.coeff_mat,rounded)-b)
            if error > 1e-5:
                raise ValueError("Error in the solution of the system.")
            self.decomp_collection.add(rounded.reshape(-1),dim,prime)
            if output_message:
                print(f"Multiplicity vector computed (dim={dim}, prime={prime}).")
            

            
    def plot(self):
        # overrides the function in commutative grid
        nodes=list(self.G.nodes)
        layout={}
        for node in nodes: # coordinates of nodes in accordance with its position in the grid
            layout.update({node:node})
        #breakpoint()
        labels=nx.get_node_attributes(self.G,'num_simplices')
        nx.draw(self.G,pos=layout,with_labels=True,labels=labels,
                node_color='lightcyan', node_shape='o', 
                node_size=500,arrowsize=20)
        
    
    def info(self,index=0):
        print(f"Dimension: {self.multiplicity_vectors[index].dim}")
        #print(f"Characteristic: {self.multiplicity_vectors[index].prime}.")
        for k,v in self.multiplicity_vectors[0].array.items():
            if v!=0:
                print(f"{k}:{v}")
        

# @timeit
# def flow():
#     temp=CommutativeLadder(4,"fff")
#     temp.sc_fill(size=100,radius_max=0.3,method='alpha')
#     temp.multiplicity_computation(dim=1)
#     vec=temp.multiplicity_vectors[0]
#     return temp

# @timeit
# def pipeline(size,method):
#     temp=CommutativeLadder(4,"fff")
#     temp.sc_fill(size=size,radius_max=0.3,method=method)
#     temp.multiplicity_computation(dim=0)
#     temp.multiplicity_computation(dim=1)
#     temp.multiplicity_computation(dim=2)
#     temp.multiplicity_vectors[0].statistics()
#     temp.multiplicity_vectors[1].statistics()
#     return temp
    

    
if __name__ == '__main__':
    size=4
    fcc_d1_alpha=thinning_pipeline('fcc',parameter_array=[1.334,1.501,2.01,2.1],parameter_type='squared',deletion_rate=0.05,dimension=1,num=size,method='alpha')
    hcp_d1_alpha=thinning_pipeline('hcp',parameter_array=[1.334,1.501,2.01,2.1],parameter_type='squared',deletion_rate=0.6,dimension=1,num=size,method='alpha')
