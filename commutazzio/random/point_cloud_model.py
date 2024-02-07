from commutazzio.filtration import SimplexTree, CLFiltration
from commutazzio.filtration import pointCloud2Filtration, random_vertical_removal_points_only
from commutazzio.compute import CLInvariants
import numpy as np
from icecream import ic
import pandas as pd
from io import StringIO
import random

def join_and_unique(arr1, arr2, precision=3):
    """
    Join two arrays into a single, sorted array without duplicates, rounding to a specified precision.

    Parameters
    ----------
    arr1 : array_like
        First input array.
    arr2 : array_like
        Second input array.
    precision : int, optional
        The decimal precision to round to before removing duplicates. Defaults to 3.

    Returns
    -------
    numpy.ndarray
        A sorted, unique array resulting from the concatenation of `arr1` and `arr2`, 
        with values rounded to the specified precision.
    """
    arr = np.concatenate((arr1, arr2))
    arr_rounded = np.around(arr, decimals=precision)
    unique_rounded, indices = np.unique(arr_rounded, return_index=True)
    return np.sort(arr[indices])

class RandomFiltrationPointCloudModel:
    """
    A class to generate random commutative ladder filtrations using the Point Cloud Model, 
    aiming to facilitate the search for non-intervals. 

    Parameters
    ----------
    num_pts : int, optional
        The number of points in the generated point cloud. Defaults to 50.
    space_dim : str or int, optional
        The dimensionality of the space for the point cloud. If "random", 
        chooses randomly between 2 and 3. Defaults to "random".
    ladder_length_min : int, optional
        The minimum ladder length for the filtration. Defaults to 4.
    ladder_length_max : int, optional
        The maximum ladder length for the filtration. Defaults to 50.
    enable_multi_processing : bool, optional
        Enables multiprocessing if True. Defaults to False.
    num_cores : str or int, optional
        The number of cores to use for multiprocessing. "auto" for automatic 
        selection. Defaults to "auto".
    verbose : bool, optional
        Enables verbose output if True. Defaults to False.

    Attributes
    ----------
    output : dict
        A dictionary holding the generated CL(4) and CL(n) filtrations if any non-trivial 
        decomposition or non-empty connected persistence diagrams are found.
    cPD : pandas.DataFrame
        The connected persistence diagram of the CL(n) filtration.

    Methods
    -------
    __init__(self, num_pts=50, space_dim="random", ladder_length_min=4, 
             ladder_length_max=50, enable_multi_processing=False, 
             num_cores="auto", verbose=False)
        Initializes the RandomNISearch instance, generates point clouds, computes filtrations, 
        and their connected persistence diagrams.

    Notes
    -----
    The class dynamically generates point clouds based on specified parameters, 
    computes filtrations for these clouds, and then analyzes them to produce 
    connected persistence diagrams. It uses the SimplexTree structure for 
    persistence computation and CLInvariants for decomposition analysis.
    """
    def __init__(self,num_pts=50,space_dim="random",ladder_length_min=4,ladder_length_max=50,enable_multi_processing=False,num_cores="auto",verbose=False):
        self.output={"CL(4)":None,"CL(n)":None}
        if space_dim == "random":
            space_dim=np.random.choice([2,3])
        if space_dim == 2:
            homology_dim = 1
        elif space_dim == 3:
            homology_dim = np.random.choice([1,2]) # randomly choose between 1 and 2
        ladder_length=random.randint(ladder_length_min,ladder_length_max) # inclusive
        upper_layer_pc=np.random.random([num_pts,space_dim]) # point cloud will be saved as long as the homology module is non-trivial
        
        # got to each branch with probability 0.5
        if False: #np.random.choice([True,False]):
            indices_removal=random_vertical_removal_points_only(num_pts=num_pts,ladder_length=len(critical_radii))
        else:
            # generate a list of random length (<num_pts) consists of integers from range(num_pts)
            # only constant removal for now
            indices_removal=sorted(np.random.choice(num_pts,size=np.random.randint(1,num_pts),replace=False))
        
        lower_layer_pc=np.delete(upper_layer_pc,indices_removal,axis=0)
        persistence_upper = SimplexTree()
        persistence_lower = SimplexTree()
        persistence_upper.from_point_cloud(upper_layer_pc,method='cech',sc_dim_ceil='auto',radius_max=np.inf)
        persistence_lower.from_point_cloud(lower_layer_pc,method='cech',sc_dim_ceil='auto',radius_max=np.inf)
        
        # compute the critical radii of both layers, join distinct values together and sort them
        critical_radii_all = join_and_unique(persistence_upper.critical_radii(dimension=homology_dim),persistence_lower.critical_radii(dimension=homology_dim) )
        # critical_radii = persistence.filtration_values
        if len(critical_radii_all) < 4:
            # skip this one
            if verbose:
                print(f'critical radii length {len(critical_radii_all)} is less than {4}')
            return
        elif 4 <= len(critical_radii_all) < ladder_length:
            # randomly choose a subset of critical radii
            if verbose:
                print(f'reducing ladder length to {len(critical_radii_all)}.')
            ladder_length = len(critical_radii_all)
        critical_radii_selected = np.sort(np.random.choice(critical_radii_all,size=ladder_length,replace=False))
        filt_n = pointCloud2Filtration(upper_layer_pc,indices_removal,radii=critical_radii_selected,max_simplex_dim=homology_dim+1)
        if verbose:
            print(f'Filtration generated.')
        filt_n.info_update({'space_dim':space_dim,'homology_dim':homology_dim,'num_pts':num_pts,'pt_cloud':upper_layer_pc.tolist(),'critical_radii_number':len(critical_radii_all)})
        if ladder_length > 4:
            filt_4=filt_n.set_new_length(4)
        else:
            filt_4=filt_n

        # compute CL(4)
        inv_4 = CLInvariants(filt_4,enable_multi_processing=enable_multi_processing,num_cores=num_cores)
        if verbose:
            print('Computing total decomposition')
            print(f'Size: upper {len(inv_4.clf.upper.maximum_simplicial_complex)}.')
            print(inv_4.clf.upper.maximum_simplicial_complex)
        inv_4.total_decomposition_computation(dim=homology_dim,prime=2)
        if verbose:
            print('computation of total decomposition done')
        if decomp:=inv_4.decompositions_all[0].nonzero_components:
            filt_4.info_update({'decomp':decomp})
            self.output.update({'CL(4)':filt_4})
            # only when there is a non-trivial decomposition
            # compute the connected persistence diagram of cl4
            inv_4.cPD_computation(homology_dim=homology_dim)
            cPD_4=inv_4.connected_persistence_diagrams[0]
            filt_4.info_update(cPD_4.plot_data)   
        # compute the connected persistence diagram of cln
        inv_n = CLInvariants(filt_n,enable_multi_processing=enable_multi_processing,num_cores=num_cores)
        inv_n.cPD_computation(homology_dim=homology_dim)
        cPD_n=inv_n.connected_persistence_diagrams[0]
        self.cPD=cPD_n
        # if (cPD.plot_data['lines'].multiplicity<0).any():
        # add to output if either lines or dots are not empty
        if not pd.read_csv(StringIO(cPD_n.plot_data['lines']),index_col=0).empty or not pd.read_csv(StringIO(cPD_n.plot_data['dots']),index_col=0).empty:
            if verbose:
                print('adding non-empty cPD to output')
            filt_n.info_update(cPD_n.plot_data)
            self.output.update({'CL(n)':filt_n})