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
from .courses import courses_cl3, courses_cl4,coeff_mat
from .decomposition_container import DecompositionCollection
from ..utils import timeit
from os import cpu_count
from joblib import delayed, Parallel
from collections import OrderedDict
from cpes import *
# import gudhi as gd
# from gtda.externals import CechComplex

cl4_equi_isoclasses=[f"N{i}" for i in range(1,22)]+[f"I{i}" for i in range(1,56)]


class CommutativeLadderQuiver(CommutativeGrid2DQuiver):
    """
    Equi-oriented by default
    """
    def __init__(self,m:int,orientation:str='equi',one_based=True,verbose=False):
        super().__init__(m,2,orientation=orientation,one_based=one_based,verbose=verbose)
        if orientation in ['equi','ff','fff']: # Specify the tours for the two cases below
            if m==3:
                self.courses_list=courses_cl3(one_based=one_based)
            elif m==4:
                self.courses_list=courses_cl4(one_based=one_based)
                self.coeff_mat=coeff_mat
        self.decomp_collection=DecompositionCollection()
        self.courses=OrderedDict((f"t_{i+1}",course) for (i,course) in enumerate(self.courses_list))
        del(self.courses_list)

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
    
    #@timeit
    def tours_vector(self,dim,prime,enable_multi_processing,num_cores):
        """
        Returns the vector of all the tours over the simplicial complex.
        mp_method: multiprocessing method, 0 for none, 1 for pool
        num_cores: int or 'auto'
        """
        m=self.shape[0]
        if set(self.orientation)!={'f'} or (m!=3 and m!=4):
            raise NotImplementedError("Incompatible orientation.")
        total_courses=len(self.courses)
        if enable_multi_processing == False:
            vector_list = []
            for i, course in enumerate(self.courses.values()):
                # a course is a sequence of nodes
                sc_zigzag_list=self.attribute_sequence(course,"simplicial_complex")
                # obtain the corresponding nodes from course to make
                # self.multiplicity_zigzag a static method, for easier parallelization implementation
                vector = self.multiplicity_zigzag(sc_zigzag_list, dim, prime)
                vector_list.append([vector])
                if self.verbose:
                    progress = f"Progress: {i+1} / {total_courses}"
                    print(f"{progress} - tours processed.",flush=True)
            # vector_list=[[self.multiplicity_zigzag(tour,dim,prime)] for tour in self.tours.values()]
        elif enable_multi_processing == True:
            max_cores=cpu_count()
            if num_cores == 'auto':
                num_cores=int(0.5*max_cores) # use half number of total cores
            elif num_cores > max_cores:
                print(f"Number of cores specified ({num_cores}) is larger than the maximum number of cores ({max_cores}).")
                print(f"Resetting number of cores to {max_cores}.")
                num_cores=max_cores
            if num_cores < 2:
                Warning("Multiprocessing is activated but number of cores is less than 2.")
            print('Number of cores being used:',num_cores)
            params = [(self.attribute_sequence(course,"simplicial_complex"),dim,prime) for course in self.courses.values()]
            from ..utils import tqdm_joblib
            from tqdm import tqdm
            # add prompt telling that the progress bar is for xxxx
            print(f"Computing multiplicity vector @ dim={dim} with prime={prime}...")
            with tqdm_joblib(tqdm(desc="Progress",total=total_courses)) as progress_bar:
                results = Parallel(n_jobs=num_cores)(delayed(self.multiplicity_zigzag)(*param) for param in params)
            # results = Parallel(n_jobs=8)(delayed(self.multiplicity_zigzag)(*param) for param in params)
            # results= Parallel(n_jobs=2)(delayed(self.computePD)(param) for param in params)
            # with Pool() as pool: # the same as Pool(os.cpu_count())
            #     results=pool.map(self.multiplicity_zigzag,params)
            vector_list = [[result] for result in results]
        else:
            raise NotImplementedError("Incompatible mp_method.")
        vector=np.array(vector_list)
        return vector.astype(int)

        

    def multiplicity_computation(self,dim=1,prime=2,recalculate=False,output_message=True,enable_multi_processing=False,num_cores=1):
        """Return the vector of multiplicities"""
        
        if len(self.decomp_collection.dim(dim).prime(prime).collection)!=0 and not recalculate:
            print("Data already exists. Use `recalculate=True` to force recalculation.")
        else:
            b=self.tours_vector(dim=dim,prime=prime,enable_multi_processing=enable_multi_processing,num_cores=num_cores)
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
    

    
# if __name__ == '__main__':
#     size=4
#     fcc_d1_alpha=thinning_pipeline('fcc',parameter_array=[1.334,1.501,2.01,2.1],parameter_type='squared',deletion_rate=0.05,dimension=1,num=size,method='alpha')
#     hcp_d1_alpha=thinning_pipeline('hcp',parameter_array=[1.334,1.501,2.01,2.1],parameter_type='squared',deletion_rate=0.6,dimension=1,num=size,method='alpha')
