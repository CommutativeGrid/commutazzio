from .commutative_ladder_quiver import CommutativeLadderQuiver as CLQ
from .connected_persistence_diagram import ConnectedPersistenceDiagram as cPD
from ..filtration import CLFiltration
from ..utils import create_directory, delete_file
from functools import cache
from icecream import ic
import gc

#a class for computing the following invariants:
# 1. total decomposition if finite-type
# 2. connected persistence diagram if infinite-type


class CLInvariants:
    def __init__(self, clf: CLFiltration,\
                 enable_multi_processing:bool=False,\
                    num_cores:int=-1,algorithm_phat:str="chunk_reduction",verbose:bool=False):
        self.clf = clf
        if len(clf) in [3,4]:
            self.quiver = CLQ(len(clf),verbose=verbose)
            self.repr_filled = False
            self.ladder_type = "finite"
        else:
            self.ladder_type = "infinite"
        self.connected_persistence_diagrams = []
        create_directory('./filtration')
        self._filtration_file_ready = False
        self._enable_multi_processing = enable_multi_processing
        self._num_cores = num_cores
        self._algorithm_phat = algorithm_phat
        self._verbose = verbose


    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self._filtration_file_ready:
            self.delete_filtration_file()
            self._filtration_file_ready = False
        for diagram in self.connected_persistence_diagrams:
            del diagram
        self.connected_persistence_diagrams = []
        gc.collect()


    def __del__(self):
        if self._filtration_file_ready:
            self.delete_filtration_file()
            self._filtration_file_ready = False
        for diagram in self.connected_persistence_diagrams:
            del diagram
        self.connected_persistence_diagrams = []
        gc.collect()

    
    @property
    def cPDs(self):
        return self.connected_persistence_diagrams
    
    def cPD_computation(self,homology_dim=1):
        """
        Compute the connected persistence diagram of the filtration at dimension dim.
        The coefficient field is GF(2). (using FZZ)
        (Can choose other finite field if we use dionysus2)
        """
        print(f"Computing connected persistence diagram at homology dimension {homology_dim}")
        if self._filtration_file_ready == False:
            self.filtration_filepath=self.clf.random_cech_format_output_file(new_file=True,dirname='./filtration',extension='fltr')
            self._filtration_file_ready = True
        params={
            'filtration_filepath':self.filtration_filepath,
            'ladder_length':self.clf.ladder_length,
            'homology_dim':homology_dim,
            'filtration_values':self.clf.horizontal_parameters,
            'enable_multi_processing':self._enable_multi_processing,
            'num_cores':self._num_cores,
            'algorithm_phat':self._algorithm_phat,
            'verbose':self._verbose
        }
        new_diagram=cPD(**params)
        self.connected_persistence_diagrams.append(new_diagram)

    def delete_filtration_file(self):
        if self._filtration_file_ready == False:
            print("Filtration file not generated yet.")
            return
        try:
            delete_file(self.filtration_filepath)
            self._filtration_file_ready = False
            print("Filtration file deleted.")
        except Exception as e:
            print(f"Error: {e}")
        return 

    @cache
    def upper_sc_array(self):
        return [self.clf.get_simplicial_complex(*(x,2)) for x in range(1,len(self.clf)+1)]

    @cache
    def lower_sc_array(self):
        return [self.clf.get_simplicial_complex(*(x,1)) for x in range(1,len(self.clf)+1)]
    
    def repr_generation(self):
        self.quiver.filtration_input(self.upper_sc_array(),self.lower_sc_array())
        self.repr_filled = True
    

    def total_decomposition_computation(self,dim=1,prime=2,recalculate=False,output_message=True):
        if self.ladder_type == "infinite":
            raise ValueError("Total decomposition is only available for finite-type commutative ladders.")
        if not self.repr_filled:
            self.repr_generation()
        self.quiver.multiplicity_computation(dim=dim,prime=prime,recalculate=recalculate,output_message=output_message,enable_multi_processing=self._enable_multi_processing,num_cores=self._num_cores)
        if self._verbose:
            print(f"Total decomposition of the homology module at dimension {dim} and finite field F{prime} is computed.")
        
    @property
    def decompositions_all(self):
        """
        Return a list of all decompositions computed.
        """
        return self.quiver.decomp_collection.collection
    
    # @property
    # def decompositions_nonzero(self):
    #     """
    #     Return a list of all nonzero components in decompositions computed.
    #     """
    #     return [decomp.nonzero_components_with_info for decomp in self.decompositions_all]
    
    # @property
    # def decompositions_nonzero_noninterval(self):
    #     """
    #     Return a list of all nonzero components in decompositions computed.
    #     """
    #     ...
    

