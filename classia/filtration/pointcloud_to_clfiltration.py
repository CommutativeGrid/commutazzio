from .simplex_tree import SimplexTree
import numpy as np
import pdb
from .clfiltration import CLFiltration



def pointCloud2Filtration(pts:np.array,vertical_removal,radii:list):
    """
    Convert a point cloud to a commutative ladder filtration.
    """
    # create a simplex tree
    # truncation it using radius in radii, get a sc
    # create upper row and lower row
    # add simplices in sc to upper row, at the designated radius
    # add simplices in sc.delete(vertical_removal[i]) to lower row, at the designated radius
    # return necessary infos
    if isinstance(vertical_removal,int):
        vertical_removal=[(vertical_removal,)]*len(radii)
    else:
        assert len(vertical_removal)==len(radii)
    parentalST=SimplexTree()
    parentalST.from_point_cloud(pts)
    upper=SimplexTree()
    lower=SimplexTree()
    for i,radius in enumerate(radii):
        x_coord=i+1
        sc=parentalST.truncation(radius)
        # pdb.set_trace()
        for simplex in sc.simplices:
            upper.insert(simplex,x_coord)
        for simplex in sc.delete_simplices(vertical_removal[i]).simplices:
            lower.insert(simplex,x_coord)
    
    return CLFiltration(upper=upper,lower=lower,length=len(radii),h_params=radii,metadata={'vertical_removal':vertical_removal})