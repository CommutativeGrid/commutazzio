from .commutative_ladder_quiver import CommutativeLadderQuiver as CLQ
from .connected_persistence_diagram import ConnectedPersistenceDiagram as cPD
from ..filtration import CLFiltration
from ..utils import create_directory
import tempfile
from functools import cache

#a class for computing the following invariants:
# 1. total decomposition if finite-type
# 2. connected persistence diagram if infinite-type


class CLInvariants:
    def __init__(self, clf: CLFiltration):
        self.clf = clf
        self.quiver = CLQ(len(clf))
        self.repr_filled = False
        if len(clf) in [3,4]:
            self.ladder_type = "finite"
        else:
            self.ladder_type = "infinite"
        self.connected_persistence_diagrams = []
        create_directory('./filtration')
        self.filtration_file_ready = False



    @property
    def cPDs(self):
        return self.connected_persistence_diagrams
    
    def cPD_computation(self,dim=1):
        """
        Compute the connected persistence diagram of the filtration at dimension dim.
        The coefficient field is GF(2). (using FZZ)
        (Can choose other finite field if we use dionysus2)
        """
        if self.filtration_file_ready == False:
            self.filtration_filepath=self.clf.random_cech_format_output_file(new_file=True,dirname='./filtration',suffix='fltr')
            self.filtration_file_ready = True
        new_diagram=cPD(self.filtration_filepath,\
                        ladder_length=self.clf.ladder_length,\
                        dim=dim,\
                        radii=self.clf.horizontal_parameters)
        self.connected_persistence_diagrams.append(new_diagram)

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
        self.quiver.multiplicity_computation(dim=dim,prime=prime,recalculate=recalculate,output_message=output_message)
        print(f"Total decomposition of the homology module at dimension {dim} and finite field F{prime} is computed.")
        
    @property
    def decompositions_all(self):
        """
        Return a list of all decompositions computed.
        """
        return self.quiver.decomp_collection.collection
    
    @property
    def decompositions_nonzero(self):
        """
        Return a list of all nonzero components in decompositions computed.
        """
        return [decomp.nonzero_components_with_info for decomp in self.decompositions_all]
    
