#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  1 14:46:51 2021

@author: kasumi
"""
#import dionysus as d
import numpy as np
import gudhi as gd
import dionysus as d
import homcloud.interface as hc


from cpes import FaceCenteredCubic as fcc_stacking
from cpes import HexagonalClosePacking as hcp_stacking
from cpes import *
from scipy.spatial.distance import cdist
from gtda.externals import CechComplex
from dataclasses import dataclass
from math import sqrt

from format_conversion import *

"""
Parameters:
    number of atoms: ~ 5000 (図6 は約5 000 原子のfcc 構造，hcp 構造から
ランダムに原子を間引いた系についてのパーシステント
図の変化を示したものである．)
    radius of sphere: should be 1 (原子間距離を 2.0 とした)
"""

@dataclass
class pd_multiplicity:
    dim: int #np.int64
    birth: float #np.float
    death: float
    count: int

class PD_packings:
    """
    collection of persistence diagrams of the input three-dimensional data
    """
    def __init__(self, packing, deletion_rate = 0, method='alpha',characteristic=2):
        if type(packing) is np.ndarray:
            self.points=packing
            self.name="packing"
            
        elif packing.__class__.__bases__[0].__name__ == 'ClosePacking':
            self.points=packing.data
            self.name=type(packing).__name__
        else:
            raise NotImplementedError()
        if deletion_rate != 0:
            num_remained=int((1-deletion_rate)*(len(self.points)))
            survivors=np.random.choice(range(len(self.points)),num_remained,replace=False)
            self.points=self.points[survivors]
            
        self.characteristic = characteristic
        self.method = method
        
        if method == 'alpha':
            s_complex = gd.AlphaComplex(points=self.points)
            simplex_tree = s_complex.create_simplex_tree()
            if simplex_tree.make_filtration_non_decreasing():
                raise ValueError("Generated raw alpha filtration not valid.")
            result_str = 'Alpha complex is of dimension ' + repr(simplex_tree.dimension())
            print(result_str)
            self.diagrams = simplex_tree.persistence(homology_coeff_field=self.characteristic)
            self.simplex_tree=simplex_tree
        elif method == 'cech':
            max_radius = np.inf
            s_complex = CechComplex(points=self.points,max_radius=max_radius)
            simplex_tree = s_complex.create_simplex_tree(max_dimension=3)
            simplex_tree.make_filtration_non_decreasing() # make sure that the generate filtration is valid
            result_str = 'Cech complex is of dimension ' + repr(simplex_tree.dimension())
            print(result_str)
            self.diagrams = simplex_tree.persistence(homology_coeff_field=self.characteristic)
            self.simplex_tree=simplex_tree
        # elif method == 'cech_dionysus':
        #     max_radius = 10
        #     s_complex = CechComplex(points=self.points,max_radius=max_radius)
        #     simplex_tree = s_complex.create_simplex_tree(max_dimension=3)
        #     result_str = 'Cech complex is of dimension ' + repr(simplex_tree.dimension())
        #     print(result_str)
        #     cech_filtration_dionysus=filtration_g2d(simplex_tree)
        #     m=d.homology_persistence(cech_filtration_dionysus,prime=self.characteristic)
        #     dgms=d.init_diagrams(m,cech_filtration_dionysus)
        #     self.diagrams = diagrams_d2g(dgms)
        #     #self.simplex_tree=simplex_tree
        elif method == 'rips':
            # radius here is 2 times the radius used to construct the sphere
            max_edge_length=np.inf
            s_complex = gd.RipsComplex(points=self.points, max_edge_length=max_edge_length)
            simplex_tree = s_complex.create_simplex_tree(max_dimension=3)
            if simplex_tree.make_filtration_non_decreasing():
                raise ValueError("Generated raw rips filtration not valid.")
            result_str = 'Rips complex is of dimension ' + repr(simplex_tree.dimension())
            print(result_str)
            self.diagrams = simplex_tree.persistence(homology_coeff_field=self.characteristic)
            self.simplex_tree=simplex_tree
        elif method == 'homcloud':
            #using alpha complex
            pdlist=hc.PDList.from_alpha_filtration(self.points,no_squared=True)
            print("Computation of pdlist finished.")
            self.diagrams=[]
            for i in range(3):
                pd = pdlist.dth_diagram(i)
                for birth,death in zip(pd.births,pd.deaths):
                    self.diagrams.append((i,(birth,death)))
        self.reduced_diagram = self.diagram_multiplicity_count(self.diagrams,data_type="gudhi")
        self.diagram_0_r = [(birth,death,count) for (dim,(birth,death),count) in self.reduced_diagram if dim==0]
        self.diagram_1_r = [(birth,death,count) for (dim,(birth,death),count) in self.reduced_diagram if dim==1]
        self.diagram_2_r = [(birth,death,count) for (dim,(birth,death),count) in self.reduced_diagram if dim==2]
    
    def filtration(self):
        """get the filtration"""
        if self.method == "homcloud":
            raise NotImplementedError("Not supported yet.")
        else:
            for i in self.simplex_tree.get_filtration():
                print(i)
        
    def info(self,dimensions=[0,1,2],epsilon=1e-3,prune=True,number_output=10):
        """return significant points in all the persistence diagrams
        epsilon is the threshold of lifetime
        """
        i=0
        if type(dimensions) is int:
            dimensions=[dimensions]
        if prune:
            values=[(dim,(birth,death),count,-count) for (dim,(birth,death),count) in self.reduced_diagram if death-birth>epsilon]
            dtype=[('dimension',int),('pair',tuple),('count',int),('-count',int)]
            PDs=np.array(values,dtype=dtype)
            PDs=np.sort(PDs,order=['dimension','-count'])
            previous_dim=0
            for (dim,(b,d),count,_) in PDs:
                if dim not in dimensions:
                    continue
                if dim!=previous_dim:
                    i=0
                if i>number_output:
                    continue
                print(f"Dimension {dim}: ({np.round(b,4)},{np.round(d,4)}), count={count}")
                i+=1
                previous_dim=dim
        else:
            PDs=[]
            PDs.append(self.diagram_0_r)
            PDs.append(self.diagram_1_r)
            PDs.append(self.diagram_2_r)
            breakpoint()
            for (i,PD) in enumerate(PDs):
                for (b,d,c) in PD:
                    print(f"Dimension {i}: ({b},{d}), count={c}")


    #TODO use heat plot
    def plot_0D(self,reduced=True,plotrange=(0,3)):
        if reduced:
            diagram=self.diagram_0_r
        else:
            diagram=[(birth,death) for (dim,(birth,death)) in self.diagrams if dim==0]
        self._plot_diagram(diagram,plotrange)

    def plot_1D(self,reduced=True,plotrange=(0,3)):
        if reduced:
            diagram=self.diagram_1_r
        else:
            diagram=[(birth,death) for (dim,(birth,death)) in self.diagrams if dim==1]
        self._plot_diagram(diagram,plotrange)

    def plot_2D(self,reduced=True,plotrange=(0,3)):
        if reduced:
            diagram=self.diagram_2_r
        else:
            diagram=[(birth,death) for (dim,(birth,death)) in self.diagrams if dim==2]
        self._plot_diagram(diagram,plotrange)
        
    
    def _plot_diagram(self,points,plotrange):
        points = [pt for pt in points if plotrange[0]<=pt[0]<plotrange[1]] # remove high values
        ax = gd.plot_persistence_diagram(points,legend=True)
        ax.set_title(f"Persistence diagram of {self.name}")
        ax.set_aspect("equal")

    #TODO use np.around instead
    @staticmethod
    def isclose(point,array):
        #breakpoint()
        if len(array)==0:
            return False
        euclidean_distance=cdist([point,],array)
        return np.isclose(euclidean_distance,0,rtol=1e-2,atol=1e-2).any()

    def _count(self,array):
        rounded=[]
        with_count=[]
        count=1
        for x in array:
            if x[0]>1e5:
                if self.method == 'homcloud':
                    continue
            if self.isclose(x,rounded):
                count+=1
            else:
                rounded.append(x)
                with_count.append((x,count))
                count=1
        return with_count
    
    def diagram_multiplicity_count(self,diagrams,data_type="gudhi"):
        if  data_type == "gudhi":
            diagram_0 = [(birth,death) for (dim,(birth,death)) in diagrams if dim==0]
            diagram_1 = [(birth,death) for (dim,(birth,death)) in diagrams if dim==1]
            diagram_2 = [(birth,death) for (dim,(birth,death)) in diagrams if dim==2]
        elif data_type == "dionysus":
            diagram_0=[(x.birth,x.death) for x in diagrams[0]]
            diagram_1=[(x.birth,x.death) for x in diagrams[1]]
            diagram_2=[(x.birth,x.death) for x in diagrams[2]]
        reduced_diagram_0 = self._count(diagram_0)
        reduced_diagram_1 = self._count(diagram_1)
        reduced_diagram_2 = self._count(diagram_2)
        reduced_diagram = [(0,*elt) for elt in reduced_diagram_0]
        reduced_diagram.extend([(1,*elt) for elt in reduced_diagram_1])
        reduced_diagram.extend([(2,*elt) for elt in reduced_diagram_2])
        return reduced_diagram
    
    def dionysus_diagram_rips(self):
        """
        Using rips complex
        """
        points=self.points
        max_edge_length=4.0
        f = d.fill_rips(points, k=3, r=max_edge_length)
        p = d.homology_persistence(f,prime=self.characteristic)
        dgms = d.init_diagrams(p, f)
        self.dgms_d=self.diagram_roundup(dgms,data_type="dionysus")
    
    def omnifield_persistence_primes(self):
        """
        return outstanding primes
        https://mrzv.org/software/dionysus2/tutorial/omni-field.html
        """
        f=filtration_g2d(self.simplex_tree)
        ofp=d.omnifield_homology_persistence(f)
        print("Outstanding primes:")
        return ofp.primes()
        
    def dionysus_result(self):
        for i, pt in self.dgms_d:
            print(i, pt[0], pt[1])



if __name__ == '__main__':
    size=10
    fcc=fcc_stacking(size,radius=1)# stacking version 
    #hcp1=hcp_cell(17,sphere_radius=1) #cell version
    hcp=hcp_stacking(size,radius=1) #stacking version
    #au=PD_packings(fcc_au,method='alpha')
    #fcc100=PD_packings(fcc,method='homcloud')
    #hcp100=PD_packings(hcp,method='homcloud')
    #fcc75=PD_packings(fcc,method='homcloud',deletion_rate=0.25)
    #hcp75=PD_packings(hcp,method='homcloud',deletion_rate=0.25)
    fcc50=PD_packings(fcc,method='homcloud',deletion_rate=0.5)
    hcp50=PD_packings(hcp,method='homcloud',deletion_rate=0.5)
    #fcc25=PD_packings(fcc,method='homcloud',deletion_rate=0.75)
    #hcp25=PD_packings(hcp,method='homcloud',deletion_rate=0.75)
    #fcc_alpha=PD_packings(fcc,method='alpha')
    fcc_hc=PD_packings(fcc,method='homcloud')
    #hcp_alpha=PD_packings(hcp,method='alpha')
    #fcc_cech=PD_packings(fcc,method='cech')
    #fcc_cech_d=PD_packings(fcc,method='cech_dionysus')
    hcp_hc=PD_packings(hcp,method='homcloud')
    #hcp_cech=PD_packings(hcp,method='cech')
    #fcc_rips=PD_packings(fcc,method='rips')
    #hcp_rips=PD_packings(hcp,method='rips')
    #auc=PD_packings(a,method='cech')
    #pd_fcc=PD_packings(fcc,method='alpha')
    #pd_hcp=PD_packings(hcp)
    #test=PD_packings(fcc,method='homcloud')

    
# =============================================================================
#     fcc_alphas=[PD_packings(fcc1,method='alpha'),PD_packings(fcc2,method='alpha')]
#     hcp_alphas=[PD_packings(hcp1,method='alpha'),PD_packings(hcp2,method='alpha')]
#     fcc_rips=[PD_packings(fcc1,method='rips'),PD_packings(fcc2,method='rips')]
#     hcp_rips=[PD_packings(hcp1,method='rips'),PD_packings(hcp2,method='rips')]
# =============================================================================
    

    #f=PD_packings(fcc,method='rips')
    #h=PD_packings(hcp,method='rips')
    #f.dionysus_diagram_rips()
    #ofp=f.omnifield_persistence()
    

    