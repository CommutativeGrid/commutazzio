from gudhi import SimplexTree as gudhi_SimplexTree
from .simplicial_complex import SimplicialComplex
import numpy as np
from scipy.spatial import distance
from gtda.externals import CechComplex
from gudhi import RipsComplex, AlphaComplex

class SimplexTree(gudhi_SimplexTree):
    Epsilon = 1e-6 # for numerical comparison

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    @property
    def maximum_simplices(self):
        temp = SimplicialComplex()
        temp.from_simplices([tuple(s[0]) for s in self.get_filtration()])
        return temp
    
    def truncation(self,ceiling):
        temp = SimplicialComplex()
        temp.from_simplices([tuple(s[0]) for s in self.get_filtration() if s[1]<=ceiling])
        return temp
    
    def insert(self,simplex,filtration_value):
        super().insert(list(simplex),filtration_value)
    
    @property
    def filtration_values(self):
        return np.sort(list(set([item[1] for item in self.get_filtration()])))
    
    
    def critical_radii(self,dimension):
        self.compute_persistence()
        bdpairs=self.persistence_intervals_in_dimension(dimension)
        return sorted((1+SimplexTree.Epsilon)*bdpairs.flatten())
        

    def from_point_cloud(self,pt_cloud,method='cech',sc_dim_ceil='auto',radius_max=np.inf):
        """
        Create a simplex tree from a point cloud.
        """
        num_pts,space_dim = pt_cloud.shape
        if sc_dim_ceil == 'auto':
            sc_dim_ceil = space_dim-1  # maximum dimension of the simplicial complex.
        if method == 'rips':
            rips_complex = RipsComplex(pt_cloud,max_edge_length=radius_max)
            simplex_tree = rips_complex.create_simplex_tree(max_dimension=sc_dim_ceil)
            simplex_tree.make_filtration_non_decreasing()
        elif method == 'alpha':
            alpha_complex = AlphaComplex(points=pt_cloud)
            simplex_tree = alpha_complex.create_simplex_tree()
            simplex_tree.make_filtration_non_decreasing()
        elif method == 'cech':
            cech_complex = CechComplex(points=pt_cloud,max_radius=np.inf)
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
    
    
