from .commutative_ladder_quiver import CommutativeLadderQuiver as CLQ
from ..filtration import CLFiltration
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
        if not self.repr_filled:
            self.repr_generation()
        self.quiver.multiplicity_computation(dim=dim,prime=prime,recalculate=recalculate,output_message=output_message)
        print(f"Total decomposition of the homology module at dimension {dim} and finite field F{prime} is computed.")
        
    @property
    def invariants(self):
        return self.quiver.decomp_collection.collection
    
    @property
    def non_zero_invariants(self):
        return [inv.nonzero_components_with_info for inv in self.invariants]
    

