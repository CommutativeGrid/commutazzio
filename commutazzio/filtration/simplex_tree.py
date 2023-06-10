from gudhi import SimplexTree as gudhi_SimplexTree
from .simplicial_complex import SimplicialComplex
import numpy as np
from scipy.spatial import distance
from gtda.externals import CechComplex
from gudhi import RipsComplex, AlphaComplex
from bisect import bisect_left

class SimplexTree(gudhi_SimplexTree):
    Epsilon = 1e-10 # for numerical comparison

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    #TODO: use a classmethod for initialization?
    # see https://medium.com/techtofreedom/9-python-built-in-decorators-that-optimize-your-code-significantly-bc3f661e9017

    def __str__(self):
        return str(list(self.get_filtration()))
        # can use ast.literal_eval to convert it back to a list of tuples

    def to_ordinal_number_indexing(self,fvs:list):
        """
        Rescale the filtration values to ordinal numbers, starting from 1.
        Based on the input fv=[t_1,t_2,...,t_n]
        """
        new_filt_ordinal = self.__class__()
        for simplex, original_fv in self.get_filtration():
            # new fv should be the smallest index of the number in fvs that is equal or larger than original_fv
            # use bisect, notice that self.horizontal_parameters is sorted
            new_fv = bisect_left(fvs,original_fv)+1 
            # if original_fv is larger than the largest value in fvs, then it will be len(fvs)+1
            new_filt_ordinal.insert(simplex,new_fv) 
            # insert the simplex with the new filtration value, notice that it will keep the lowest value
        return new_filt_ordinal
    
    def to_custom_filtration_values(self,fvs:list):
        """
        Rescale a simplex tree with ordinal number filtration values [1,2,...,n]
        to user input filtration values.
        """
        new_filt_custom = self.__class__()
        original_fv = self.filtration_values #can be [1,3,7,...]
        original_fv_len = len(original_fv)
        
        # assert that the original filtration values are 1,2,...,
        for i in original_fv:
            if not i.is_integer() or i<1:
                raise ValueError(f'Found non-integeer or non-positive filtration value {i} in the original filtration values.')
        if len(fvs) > original_fv_len:
            #just print the message below and let the user know what is giving the warning
            pass
            # print(f"{self.__class__.__name__}{hex(id(self))}: {len(fvs)} filtration values given, while the original A_n quiver length is {original_fv_len}.")
            #warn('The number of new filtration values is greater than the count of original filtration values in the simplex tree.')
        elif len(fvs) < original_fv_len:
            print(f"{self.__class__.__name__}{hex(id(self))}: {len(fvs)} filtration values given, smaller than the original A_n quiver length {original_fv_len}.")
            # warn('The number of filtration values is smaller \
            #      than the count of original filtration values in the simplex tree.\n\
            #      simplices after the last filtration value will be ignored.')
        for simplex, original_fv in self.get_filtration():
            # new fv should be the smallest index of the number in fvs that is equal or larger than original_fv
            # use bisect, notice that self.horizontal_parameters is sorted
            original_fv_int=int(original_fv)
            if original_fv_int > len(fvs):
                break
            new_fv = fvs[original_fv_int-1]
            new_filt_custom.insert(simplex,new_fv) 
            # insert the simplex with the new filtration value, notice that it will keep the lowest value
        return new_filt_custom


    @property
    def maximum_simplices(self):
        temp = SimplicialComplex()
        temp.from_simplices([tuple(s[0]) for s in self.get_filtration()])
        return temp
    
    def truncation(self,ceiling):
        temp = SimplicialComplex()
        temp.from_simplices([tuple(s[0]) for s in self.get_filtration() if s[1]<=ceiling+SimplexTree.Epsilon])
        return temp
    
    def insert(self,simplex,filtration_value):
        super().insert(list(simplex),filtration_value)
    
    @property
    def filtration_values(self):
        return np.sort(list(set([item[1] for item in self.get_filtration()])))
    
    
    def critical_radii(self,dimension):
        self.compute_persistence()
        bdpairs=self.persistence_intervals_in_dimension(dimension)
        return sorted(np.unique((1+SimplexTree.Epsilon)*bdpairs.flatten()))
        
    def from_point_cloud(self,pt_cloud,method='cech',sc_dim_ceil='auto',radius_max=np.inf):
        """
        Create a simplex tree from a point cloud.
        """
        num_pts,space_dim = pt_cloud.shape # number of points and dimension of the space.
        # print('num_pts',num_pts,'space_dim',space_dim)
        if sc_dim_ceil == 'auto':
            sc_dim_ceil = space_dim  # maximum dimension of the simplicial complex.
        if method == 'rips':
            rips_complex = RipsComplex(pt_cloud,max_edge_length=radius_max)
            simplex_tree = rips_complex.create_simplex_tree(max_dimension=sc_dim_ceil)
            simplex_tree.make_filtration_non_decreasing()
        elif method == 'alpha':
            alpha_complex = AlphaComplex(points=pt_cloud)
            simplex_tree = alpha_complex.create_simplex_tree()
            simplex_tree.make_filtration_non_decreasing()
        elif method == 'cech':
            cech_complex = CechComplex(points=pt_cloud,max_radius=radius_max)
            simplex_tree = cech_complex.create_simplex_tree(max_dimension=sc_dim_ceil)
            simplex_tree.make_filtration_non_decreasing()
        # elif method == 'weak-witness':
        #     diameter = max(distance.cdist(pt_cloud,pt_cloud,'euclidean').flatten())
        #     witnesses=pt_cloud
        #     w_l_ratio=5
        #     n_landmarks=int(len(pt_cloud)/w_l_ratio) # vertices consist of landmarks. A too low value may cause zero candidates available for being deleted.
        #     landmarks=gd.pick_n_random_points(points=pt_cloud,nb_points=n_landmarks)
        #     witness_complex = gd.EuclideanWitnessComplex(witnesses=witnesses, landmarks=landmarks)
        #     max_alpha_square = diameter/50.0
        #     simplex_tree = witness_complex.create_simplex_tree(max_alpha_square=max_alpha_square,limit_dimension=sc_dim_ceil)
        #     simplex_tree.make_filtration_non_decreasing()
        # elif method == 'strong-witness':
        #     diameter = max(distance.cdist(pt_cloud,pt_cloud,'euclidean').flatten())
        #     witnesses=pt_cloud
        #     w_l_ratio=5
        #     n_landmarks=int(len(pt_cloud)/w_l_ratio)
        #     landmarks=gd.pick_n_random_points(points=pt_cloud,nb_points=n_landmarks)
        #     witness_complex = gd.EuclideanStrongWitnessComplex(witnesses=witnesses, landmarks=landmarks)
        #     max_alpha_square = diameter/50.0
        #     simplex_tree = witness_complex.create_simplex_tree(max_alpha_square=max_alpha_square,limit_dimension=sc_dim_ceil)
        #     simplex_tree.make_filtration_non_decreasing()
        else:
            raise NotImplementedError('Method not supported.')
        # reconstruct the simplex tree from the gudhi simplex tree.
        for simplex,value in simplex_tree.get_filtration():
            self.insert(simplex,value)


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
            return self.from_point_cloud(pt_cloud,method=method,sc_dim_ceil=sc_dim_ceil,radius_max=radius_max)
    
    
