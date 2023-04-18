from .simplex_tree import SimplexTree
import numpy as np
from .clfiltration import CLFiltration
from random import randint #inclusive of the upper bound

def random_vertical_removal_points_only(num_pts,ladder_length,max_removal_per_time=None):
    # generate a list of length ladder_length
    # each item is a list of tuples representing points to be removed, indices of points is in range(0,num_pts)
    # an later item shall contain all the simplices of the previous item
    # for example, if ladder_length=3, and num_pts = 10, an output could be
    # [[(0,),(2,)],[(0,),(2,),(5,)],[(0,),(2,),(3,),(5,)]]
    # reverse the generated list and output
    result = []
    removed_points = []
    remained_points = list(range(num_pts))
    if max_removal_per_time is None:
        max_removal_per_time = max(1,int(num_pts/ladder_length))
    for _ in range(ladder_length):
        try:
            num_removed_points = min(\
                randint(1, \
                        min(max_removal_per_time,\
                            max(1,num_pts - len(removed_points))\
                                )\
                        ),\
                        len(remained_points)-1\
                                            )
        except ValueError:
            num_removed_points = 0
            removed_points = removed_points[-1]
        for _ in range(num_removed_points):
            #random sample from remained_points
            removed_point = remained_points.pop(randint(0,len(remained_points)-1))
            removed_points.append(removed_point)
        result.append([tuple([point]) for point in sorted(removed_points)])
    
    return result[::-1]

def pointCloud2Filtration(pts:np.array,vertical_removal:list,radii:list,max_simplex_dim:int):
    """
    Convert a point cloud to a commutative ladder filtration.
    pts: a numpy array of shape (n,d), where n is the number of points, d is the dimension of the points
    vertical_removal: a list of list of simplices to be removed at each radius, notice that it is the name of the simplices, not the indices of the simplices
    """
    # create a simplex tree
    # truncation it using radius in radii, get a sc
    # create upper row and lower row
    # add simplices in sc to upper row, at the designated radius
    # add simplices in sc.delete(vertical_removal[i]) to lower row, at the designated radius
    # return necessary infos
    if isinstance(vertical_removal[0],(int, np.int64)): #[2,3,4,5,6,7]
        vertical_removal=[[(vertex,) for vertex in vertical_removal]]*len(radii)
        print(vertical_removal)
    else:
        #example: [[(2,),(3,)],[(2,),(3,),(4,)],[(2,),(3,),(4,),(5,)]
        # canonically, vertical_removal is a list of list of simplices
        # each entry of vertical_removal is a list of simplices to be removed, for example [(1,),(2,3)]
        assert len(vertical_removal)==len(radii)
    #check that radii is sorted
    assert all(radii[i]<=radii[i+1] for i in range(len(radii)-1))
    parentalST=SimplexTree()
    parentalST.from_point_cloud(pts)
    upper=SimplexTree()
    lower=SimplexTree()
    for i,radius in enumerate(radii):
        x_coord=i+1
        sc=parentalST.truncation(radius)
        # pdb.set_trace()
        for simplex in sc.simplices:
            if len(simplex)<=max_simplex_dim+1:
                upper.insert(simplex,x_coord) 
                # this function will not make existing filtration value higher
                # This function inserts the given N-simplex 
                # and its subfaces with the given filtration value (default value is ‘0.0’). 
                # If some of those simplices are already present with a higher filtration value, 
                # their filtration value is lowered.
        for simplex in sc.delete_simplices(vertical_removal[i]).simplices:
            if len(simplex)<=max_simplex_dim+1:
                lower.insert(simplex,x_coord)
    # from icecream import ic
    # ic(parentalST.maximum_simplices)
    # ic(upper.maximum_simplices)
    # ic(lower.maximum_simplices)
    return CLFiltration(upper=upper,lower=lower,length=len(radii),h_params=radii,info={'vertical_removal':vertical_removal})