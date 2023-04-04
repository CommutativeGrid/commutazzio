#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 31 19:20:11 2021

@author: kasumi
"""

import networkx as nx
import numpy as np
import random
from .commutative_grid import CommutativeGrid2D
from .random_point_cloud_square import RandomPointCloudSquare
from ..filtration import SimplicialComplex
from .tours import tours_cl3,tours_cl4,coeff_mat
from .multiplicity_vectors import MultiplicityVectors
from ..utils import timeit
from pathos.multiprocessing import ProcessingPool as Pool
from collections import OrderedDict
from cpes import *
import gudhi as gd
from gtda.externals import CechComplex

cl4_equi_isoclasses=[f"N{i}" for i in range(1,22)]+[f"I{i}" for i in range(1,56)]


class CommutativeLadder(CommutativeGrid2D):
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
        self.multiplicity_vectors=MultiplicityVectors()
        self.tours=OrderedDict((f"t_{i+1}",tour) for (i,tour) in enumerate(self.tours_list))
        del(self.tours_list)



    #TODO:move to another class
    def sc_filtration_input(self,upper_row,lower_row):
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
        self.plot() 

        

    #TODO:move to another class
    def sc_verification_single_fill(self):
        empty_vertex=SimplicialComplex([])
        single_vertex=SimplicialComplex([(0,)])
        for node in self.G.nodes:
            values={
                node:empty_vertex.info_node()
            }
            nx.set_node_attributes(self.G, values=values)
        values={
            (4,2):single_vertex.info_node()
        }
        nx.set_node_attributes(self.G, values=values)

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

        

    def multiplicity_computation(self,dim=1,prime=2,recalculate=False,mp_method=1,output_message=True):
        """Return the vector of multiplicities"""
        
        if len(self.multiplicity_vectors.dim(dim).prime(prime).vectors)!=0 and not recalculate:
            print("Already existed. Pass parameter recalculate=True to recalculate.")
        else:
            b=self.tours_vector(dim=dim,prime=prime,mp_method=mp_method)
            result=np.linalg.solve(self.coeff_mat,b)
            rounded=result.round().astype(int)
            error=np.linalg.norm(np.matmul(self.coeff_mat,rounded)-b)
            if error > 1e-5:
                raise ValueError("Error in the solution of the system.")
            self.multiplicity_vectors.add(rounded,dim,prime)
            if output_message:
                print(f"Multiplicity vector computed (dim={dim}, prime={prime}).")
            

            
    def plot(self):
        # overrides the function in commutative grid
        nodes=list(self.G.nodes)
        layout={}
        for node in nodes: # coordinates of nodes in accordance with its position in the grid
            layout.update({node:node})
        #breakpoint()
        labels=nx.get_node_attributes(self.G,'sc_size')
        nx.draw(self.G,pos=layout,with_labels=True,labels=labels)
    
    def info(self,index=0):
        print(f"Dimension: {self.multiplicity_vectors[index].dim}")
        #print(f"Characteristic: {self.multiplicity_vectors[index].prime}.")
        for k,v in self.multiplicity_vectors[0].array.items():
            if v!=0:
                print(f"{k}:{v}")
        

@timeit
def flow():
    temp=CommutativeLadder(4,"fff")
    temp.sc_fill(size=100,radius_max=0.3,method='alpha')
    temp.multiplicity_computation(dim=1)
    vec=temp.multiplicity_vectors[0]
    return temp

@timeit
def pipeline(size,method):
    temp=CommutativeLadder(4,"fff")
    temp.sc_fill(size=size,radius_max=0.3,method=method)
    temp.multiplicity_computation(dim=0)
    temp.multiplicity_computation(dim=1)
    temp.multiplicity_computation(dim=2)
    temp.multiplicity_vectors[0].statistics()
    temp.multiplicity_vectors[1].statistics()
    return temp
    
@timeit
def thinning_pipeline(crystal_type,parameter_array,parameter_type,deletion_rate,num=10,radius=1,method='alpha',dimension=1):
    cl4m=CommutativeLadder(4,"fff")
    cl4m.point_cloud_from_crystal(crystal_type=crystal_type,num=num,radius=radius)
    cl4m.thinning_fill(method=method,parameter_array=parameter_array,parameter_type=parameter_type,deletion_rate=deletion_rate)
    if dimension == 1:
        cl4m.multiplicity_computation(dim=1)
        cl4m.multiplicity_vectors[0].statistics()
    elif dimension == 2:
        cl4m.multiplicity_computation(dim=2)
        cl4m.multiplicity_vectors[0].statistics()
    return cl4m
    
if __name__ == '__main__':
    #aa=CommutativeGrid2D(4,3)
    #aa.plot()
    #qqq=flow()
    #vecc=qqq.multiplicity_vectors[0]
    #sc=thinning_pipeline('sc','alpha',3,0.5)
    #sc=thinning_pipeline('sc','alpha',6,0.25)
    #fcc=thinning_pipeline('fcc','alpha',6,0.25)
    #bcc=thinning_pipeline('bcc','alpha',6,0.25)
    #0,1,4/3
    #fcc=thinning_pipeline('fcc',radii=[1.332,1.4,1.5,1.6],deletion_rate=0.75,dimension=1)
    #hcp=thinning_pipeline('hcp',radii=[1.332,1.4,1.5,1.6],deletion_rate=0.75,dimension=1)
    #0,4/3,1.5,2
    size=4
    fcc_d1_alpha=thinning_pipeline('fcc',parameter_array=[1.334,1.501,2.01,2.1],parameter_type='squared',deletion_rate=0.05,dimension=1,num=size,method='alpha')
    hcp_d1_alpha=thinning_pipeline('hcp',parameter_array=[1.334,1.501,2.01,2.1],parameter_type='squared',deletion_rate=0.6,dimension=1,num=size,method='alpha')
    #fcc_d1_cech=thinning_pipeline('fcc',parameter_array=[1.334,1.501,2.01,2.1],parameter_type='squared',deletion_rate=0.05,dimension=1,num=size,method='cech')
    #hcp_d1_cech=thinning_pipeline('hcp',parameter_array=[1.334,1.501,2.01,2.1],parameter_type='squared',deletion_rate=0.6,dimension=1,num=size,method='cech')
# =============================================================================
#     a=CommutativeLadder(4,"fff")
#     a.point_cloud_from_crystal('sc',6)
#     a.thinning_fill('alpha')
#     # res=[]
# =============================================================================
    # for size in range(100,200,100):
    #     print(size)
    #     a=pipeline(size,'rips')
    #     print(a.G.nodes[(4,2)]['sc'])
    #     res.append(a)
    #     print('----------')
# =============================================================================
#     holder=[]
#     for i in range(20):
#         temp=CommutativeLadder(4,"fff")
#         temp.sc_fill(size=120,radius_max=0.3)
#         temp.multiplicity_computation(dim=2)
#         vec=temp.multiplicity_vectors[0]
#         holder.append(vec)
# =============================================================================
        
    #aaa=CommutativeLadder(4,"fff")
    #aaa.sc_fill(size=150,radius_max=0.3)
    #aaa.plot()
    #res=aaa.multiplicity_computation(dim=0)
    #res=aaa.multiplicity_computation(dim=1)
    #res=aaa.multiplicity_computation(dim=2)
    #print(res)
    #nodes=[(1,1),(3,2),(2,2)]
    #d1=aaa.multiplicity(dim=1)
    #d2=aaa.multiplicity(dim=2)
    #print(d1)