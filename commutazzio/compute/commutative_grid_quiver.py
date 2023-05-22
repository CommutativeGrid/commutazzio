#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 18:03:10 2021

@author: kasumi
"""
import networkx as nx
import numpy as np
from ..filtration import ZigzagFiltration
import dionysus as d
from itertools import product

def one_based_numbering(dim_vector):
    """
        Returns the mapping rules for converting from 0-based vector to 1-based vector.
        For example, if dim_vector = [2, 2], then first we generate all 0-based points within this range,
        Then we convert them to 1-based points.
        The result will be {(0, 0): (1, 1), (0, 1): (1, 2), (1, 0): (2, 1), (1, 1): (2, 2)}
    """
    mapping={}
    for coordinate in product(*(range(_) for _ in dim_vector)):
                            
            mapping.update({coordinate:tuple(np.array(coordinate)+1)})
    
    return mapping


class CommutativeGridQuiver:
    def __init__(self,dim_vector,one_based=True):
        H=nx.grid_graph(dim_vector[::-1]).to_directed() # reverse the order,xyz-coordinate convention
        
        self.one_based=one_based
        self.offset = 1 if self.one_based else 0 #counting offset
        if self.one_based:
            self.G=nx.relabel_nodes(H, one_based_numbering(dim_vector), copy=True)
        else:
            self.G=H
        self.shape=dim_vector

    def plot(self):
        # change the direction so that it's
        # in accordance with our settings
        #pos = nx.spring_layout(self.G, iterations=100, seed=39775)
        # https://networkx.org/documentation/stable/reference/drawing.html
        nx.draw(self.G,with_labels=True)
        
    def attribute_sequence(self,nodes,attribute="simplicial_complex"):
        """
        Generate a list of attributes of the given nodes.
        """
        output=[]
        for node in nodes:
            output.append(self.G.nodes[node][attribute])
        return output
    
    @staticmethod
    def longest_matching(diagram_point):
        """Test if the given diagram point is of form (0,inf)"""
        # Remark: notice that the diagram in dionysus2 is in the form (birth,death)
        # where birth means the time when the corresponding homology class is born
        # and death means the time when the corresponding homology class dies
        # NOTICE that the homology generator DOES NOT EXIST at the time of death
        # so for any other usage other than this one, index changing is necessary
        if diagram_point.birth==0 and diagram_point.death==np.inf:
            return True
        else:
            return False

    def multiplicity_zigzag(self,zigzag_filtration_nodes,dim=1,prime=2):
        # TODO: make it a static method, for faster computation when using mp
        """
        Compute the multiplicity of the longest interval in the given
        zigzag filtration of simplicial complexes
        """
        sc_filtration=self.attribute_sequence(zigzag_filtration_nodes,"simplicial_complex")
        tour=ZigzagFiltration(*sc_filtration)
        filtration_dionysus=d.Filtration(tour.ensemble)
        times=tour.all_time_sequences()
        zz, dgms, cells = d.zigzag_homology_persistence(filtration_dionysus, times, prime=prime) # dgms in all dimensions, starting from zero
        count=0
        if dim > len(dgms)-1:
            #raise ValueError("Dimension is larger than the dimension of the simplicial complex")
            #warn("The specified dimension is larger than the dimension of the simplicial complex.")
            count=0
        else:
            count = sum(1 for p in dgms[dim] if self.longest_matching(p))
            # for p in dgms[dim]:
            #     if self.longest_matching(p):
            #         count+=1
        return count

class CommutativeGrid2DQuiver(CommutativeGridQuiver):

    def __init__(self,m:int,n:int,orientation:str='equi',one_based=True):
        """
        Generates a m by n grid
        equioriented by default
        
        Parameters
        -------
        
        m : int
            in horizontal direction
        n : int 
            in vertical (upwards) direction
        
        Returns
        -------
            
        """
        if orientation == 'equi':
            self.orientation = (m-1)*'f'
        else:
            self.orientation = orientation
        super().__init__([m,n],one_based=one_based)
        self.G.remove_edges_from(list(self.G.edges)) # remove all edges
        self.__add_edges(m,n,self.orientation)
        
    def __add_edges(self,m,n,orientation):
        edges=[]
        if len(orientation)!=m-1:
            raise ValueError("Orientation vector not compatible with the grid size.")
        if not set(orientation).issubset({'f','b'}):
            raise ValueError("Letters in orientation vector illegal.")
        
        for _,i in enumerate(range(0+self.offset,m-1+self.offset)): # over columns
            direction=orientation[_]
            for j in range(0+self.offset,n-1+self.offset): # over rows
                # Add a vertical arrow
                edges.append(
                    (
                        (i,j),
                        (i,j+1)
                    )
                    )
                # Add a horizontal arrow
                if direction == "f":
                    edges.append(
                        (
                            (i,j),
                            (i+1,j)
                        )
                        )
                elif direction == "b":
                    edges.append(
                        (
                            (i+1,j),
                            (i,j)
                        )
                        )
                    
        # vertical arrows in the last column
        for j in range(0+self.offset,n-1+self.offset): 
            edges.append(
                (
                    (m-1+self.offset,j),
                    (m-1+self.offset,j+1)
                )
                )
        
        #horizontal arrows in the uppermost row
        for _,i in enumerate(range(0+self.offset,m-1+self.offset)): # over columns
            direction=orientation[_]
            if direction == "f":
                edges.append(
                    (
                        (i,n-1+self.offset),
                        (i+1,n-1+self.offset)
                    )
                    )
            elif direction == "b":
                edges.append(
                    (
                        (i+1,n-1+self.offset),
                        (i,n-1+self.offset)
                    )
                    )
        
        self.G.add_edges_from(edges)
        
    def plot(self):
        # this function is overridden in commutative grid
        nodes=list(self.G.nodes)
        layout={}
        for node in nodes: # coordinates of nodes in accordance with its position in the grid
            layout.update({node:node})
        #breakpoint()
        nx.draw(self.G,pos=layout,with_labels=False,node_color='lightcyan', node_shape='o')


# node attributes
# https://networkx.org/documentation/stable/tutorial.html


