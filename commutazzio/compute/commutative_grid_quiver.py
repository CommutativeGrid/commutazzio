"""
This module defines classes and functions for creating commutative grid quivers, converting coordinate
numbering systems, and performing topological computations such as longest matching and multiplicity of zigzag filtrations.

Dependencies:
    - networkx: For creating and manipulating graph structures.
    - numpy: For numerical operations.
    - itertools.product: For generating Cartesian products.
    - ZigzagFiltration: Custom class from the 'filtration' module for handling zigzag filtrations.
"""
import networkx as nx
import numpy as np
from itertools import product
from ..filtration import ZigzagFiltration

def one_based_numbering(dim_vector):
    """
    Generate a mapping from 0-based to 1-based indexing for coordinates within given dimensions.
    
    Parameters:
        dim_vector (list of int): Dimension sizes for each axis of the grid.
    
    Returns:
        dict: A dictionary mapping 0-based indices to 1-based indices.
    
    Example:
        If dim_vector = [2, 2], the function returns {(0, 0): (1, 1), (0, 1): (1, 2), (1, 0): (2, 1), (1, 1): (2, 2)}.
    """
    mapping={}
    for coordinate in product(*(range(_) for _ in dim_vector)):
                            
            mapping.update({coordinate:tuple(np.array(coordinate)+1)})
    
    return mapping

def longest_matching(diagram_point):
    """
    Determine if a given diagram point is of the form (0, infinity), indicating an infinite persistence interval.
    
    Parameters:
        diagram_point: A point in the persistence diagram, typically a tuple (birth, death).
    
    Returns:
        bool: True if the point represents an infinite interval, False otherwise.
    """
    # Remark: notice that the diagram in dionysus2 is in the form (birth,death)
    # where birth means the time when the corresponding homology class is born
    # and death means the time when the corresponding homology class dies
    # NOTICE that the homology generator DOES NOT EXIST at the time of death
    # so for any other usage other than this one, index changing is necessary
    return diagram_point.birth == 0 and diagram_point.death == np.inf

class CommutativeGridQuiver:
    """
    A class to represent a directed graph (quiver) constructed from a grid, supporting commutative diagrams.
    
    Attributes:
        G (networkx.DiGraph): The directed graph representing the quiver.
        shape (list of int): The dimensions of the grid.
        one_based (bool): Flag to use 1-based indexing for grid coordinates.
    
    Methods:
        plot(): Plots the quiver using networkx drawing facilities.
        attribute_sequence(nodes, attribute): Generates a list of attributes for given nodes.
    """
    def __init__(self,dim_vector,one_based=True,verbose=False):
        """
        Initializes the CommutativeGridQuiver with a specified grid shape and indexing convention.
        
        Parameters:
            dim_vector (list of int): The dimensions of the grid, specifying size along each axis.
            one_based (bool, optional): If True, uses 1-based indexing for grid coordinates. Defaults to True.
        """
        H=nx.grid_graph(dim_vector[::-1]).to_directed() # reverse the order,xyz-coordinate convention
        
        self.one_based=one_based
        self.offset = 1 if self.one_based else 0 #counting offset
        if self.one_based:
            self.G=nx.relabel_nodes(H, one_based_numbering(dim_vector), copy=True)
        else:
            self.G=H
        self.shape=dim_vector
        self.verbose=verbose

    def plot(self):
        """
        Plots the quiver using matplotlib, with nodes labeled according to their grid coordinates.
        """
        # change the direction so that it's
        # in accordance with our settings
        #pos = nx.spring_layout(self.G, iterations=100, seed=39775)
        # https://networkx.org/documentation/stable/reference/drawing.html
        nx.draw(self.G,with_labels=True)
        
    def attribute_sequence(self,nodes,attribute="simplicial_complex"):
        """
        Generates a sequence of attributes for a given list of nodes in the quiver.
        
        Parameters:
            nodes (list): A list of node identifiers within the quiver.
            attribute (str, optional): The attribute to extract for each node. Defaults to "simplicial_complex".
        
        Returns:
            list: A list containing the specified attributes of the given nodes.
        """
        # output=[]
        # for node in nodes:
        #     # output.append(self.G.nodes[node][attribute])
        #     output.append(self.G.nodes[node][attribute].simplices)
        # return output
        return [self.G.nodes[node][attribute].simplices for node in nodes]


    @staticmethod   
    def computePD(i):
        """
        Static method (placeholder) for computing persistence diagrams, intended for compatibility testing.
        
        Parameters:
            i (int): An arbitrary input parameter for testing purposes.
        
        Returns:
            int: A random integer, simulating a computation result.
        """
        import dionysus as d
        import numpy as np
        np.random.seed(42)
        f = d.Filtration([[0], [1], [0,1], [2], [0,2], [1,2]])
        times = [[.4, .6, .7], [.1], [.9], [.9], [.9], [.9]]
        zz, dgms, cells = d.zigzag_homology_persistence(f, times)
        return np.random.randint(1,20)

    @staticmethod
    def multiplicity_zigzag(sc_zigzag_list,dim=1,prime=2):
        """
        Computes the multiplicity of the longest interval in a given zigzag filtration of simplicial complexes.
        
        Parameters:
            sc_zigzag_list (list): A list of simplicial complexes in the zigzag filtration.
            dim (int, optional): The dimension in which to compute the multiplicity. Defaults to 1.
            prime (int, optional): The prime base for field coefficients in homology computations. Defaults to 2.
        
        Returns:
            int: The multiplicity of the longest interval in the specified dimension.
        """
        import dionysus as d
        # f = d.Filtration([[0], [1], [0,1], [2], [0,2], [1,2]])
        # times = [[.4, .6, .7], [.1], [.9], [.9], [.9], [.9]]
        # zz, dgms, cells = d.zigzag_homology_persistence(f, times)
        # return dgms[1]
        # return 1
        # zzf=self.attribute_sequence(course,"simplicial_complex")
        # return 1
        tour=ZigzagFiltration(*sc_zigzag_list)
        filtration_dionysus=d.Filtration(tour.ensemble)
        times=tour.all_time_sequences()
        zz, dgms, cells = d.zigzag_homology_persistence(filtration_dionysus, times, prime=prime) # dgms in all dimensions, starting from zero
        count=0
        if dim > len(dgms)-1:
            #raise ValueError("Dimension is larger than the dimension of the simplicial complex")
            #warn("The specified dimension is larger than the dimension of the simplicial complex.")
            count=0
        else:
            count = sum(1 for p in dgms[dim] if longest_matching(p))
        return count



class CommutativeGrid2DQuiver(CommutativeGridQuiver):
    """
    A subclass of CommutativeGridQuiver for generating and manipulating 2-dimensional grid quivers.

    Attributes:
        orientation (str): A string representing the orientation of arrows between nodes in the grid.
    """

    def __init__(self,m:int,n:int,orientation:str='equi',one_based=True,verbose=False):
        """
        Initializes the CommutativeGrid2DQuiver with specified dimensions and orientation.
        
        Parameters:
            m (int): The number of columns in the grid, in the horizontal(x) direction.
            n (int): The number of rows in the grid, in vertical(y) direction
            orientation (str, optional): Specifies the orientation of horizontal arrows. 'equi' for equioriented (all forward), or a string of 'f' (forward) and 'b' (backward) characters indicating the orientation for each column. Defaults to 'equi'.
            one_based (bool, optional): If True, uses 1-based indexing for grid coordinates. Defaults to True.
        """
        if orientation == 'equi':
            self.orientation = (m-1)*'f'
        else:
            self.orientation = orientation
        super().__init__([m,n],one_based=one_based,verbose=verbose)
        self.G.remove_edges_from(list(self.G.edges)) # remove all edges
        self.__add_edges(m,n,self.orientation)
        
    def __add_edges(self,m,n,orientation):
        """
        Internal method to add edges to the grid quiver based on specified orientation.
        
        This method configures the directional edges between nodes in the grid according to the orientation
        parameter, establishing the commutative diagram structure.
        
        Parameters:
            m (int): The number of columns in the grid.
            n (int): The number of rows in the grid.
            orientation (str): A string representing the orientation of arrows.
        Raises:
            ValueError: If the orientation string length does not match the grid width minus one,
                        or if it contains characters other than 'f' or 'b'.
        """
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
        """
        Plots the 2D grid quiver using matplotlib, with nodes positioned according to their grid coordinates.
        
        This overridden method ensures that the grid is visualized in a manner consistent with its 2D structure,
        with node positions reflecting their actual locations within the grid layout.
        """
        # this function is overridden in commutative grid
        nodes=list(self.G.nodes)
        layout={}
        for node in nodes: # coordinates of nodes in accordance with its position in the grid
            layout.update({node:node})
        #breakpoint()
        nx.draw(self.G,pos=layout,with_labels=False,node_color='lightcyan', node_shape='o')


# node attributes
# https://networkx.org/documentation/stable/tutorial.html


