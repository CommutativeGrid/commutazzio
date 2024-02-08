import numpy as np

cl4_equi_intervals=[f"I{i}" for i in range(1,56)]
cl4_equi_nonintervals=[f"N{i}" for i in range(1,22)]
cl4_equi_isoclasses=cl4_equi_nonintervals + cl4_equi_intervals
#cl4_equi_isoclasses=[f"N{i}" for i in range(1,22)]+[f"I{i}" for i in range(1,56)]

#multi_vec_cl4_equi=namedtuple('cl4_equi',cl4_equi_isoclasses)


class Decomposition:
    """A namedtuple-like class to store 
    information of multiplicity values."""
    def __init__(self,mult,dim,prime):
        #self._array = multi_vec_cl4_equi(*array.flatten())
        if isinstance(mult,dict):
            # fill values existing in mult, all other values zero
            self._mult = {k:mult.get(k,0) for k in cl4_equi_isoclasses}
        elif isinstance(mult,np.ndarray):
            self._mult = {k:v for k,v in zip(cl4_equi_isoclasses, mult)}
        self._dim = dim
        self._prime = prime

    def __getitem__(self,item):
        if isinstance(item, str):
            return self._mult[item]
        elif isinstance(item, int) and 0<=item<len(cl4_equi_isoclasses):
            return self._mult[cl4_equi_isoclasses[item]]

    def to_dict(self,skip_zero:bool=True,verbose=True):
        """
        Return a json-serializable dictionary of the decomposition.

        Parameters
        ----------
        skip_zero : bool, optional
            If True, only include nonzero components in the dictionary. Default is True.
        verbose : bool, optional
            If True, print additional information. Default is True.

        Returns
        -------
        dict
            A dictionary with keys 'mult', 'dim', and 'prime', representing the 
            multiplicity, dimension, and prime components of the decomposition, respectively.
        """
        if not isinstance(skip_zero, bool):
            raise TypeError("skip_zero must be a boolean")
        if skip_zero:
            if verbose:
                print("to_dict() called with skip_zero=True, only nonzero components are returned.")
            return {
                "mult": {k: int(v) for k, v in self.nonzero_components.items()},
                "dim": int(self.dim),
                "prime": int(self.prime)
            }
        else:
            if verbose:
                print("to_dict() called with skip_zero=False, returning all components.")
            return {
                "mult": {k: int(v) for k, v in self.mult.items()},
                "dim": int(self.dim),
                "prime": int(self.prime)
            }

    @property
    def mult(self):
        return self._mult

    @property
    def m(self):
        return self._mult

    @property
    def dim(self):
        return self._dim
    
    @property
    def prime(self):
        return self._prime

    def pretty_print(self):
        """Print out the multiplicity values line by line"""
        for k,v in self._mult.items():
            print(f"{k}:{v}")

    def __repr__(self):
        return f"array: {str(self.mult)},\ndim: {str(self.dim)},\nprime: {str(self.prime)}"

    @property
    def nonzero_nonintervals(self):
        """Return non-trivial non-intervals"""
        return {k:v for (k,v) in self.mult.items() if v!=0 and k[0]=='N'}
    @property
    def nonzero_components(self):
        """Return the nonzero components of the multiplicity vector"""
        return {k:v for (k,v) in self.mult.items() if v!=0}

    # @property
    # def nonzero_components_with_info(self):
    #     """Return the nonzero components of the multiplicity vector with additional information"""
    #     return Decomposition({k:v for (k,v) in self.array.items() if v!=0},self.dim,self.prime)

        

    def statistics(self):
        """Print out the statistics of the multiplicity values"""
        count_intervals = 0
        count_nonintervals = 0
        for name in cl4_equi_intervals:
            count_intervals += self[name]
        for name in cl4_equi_nonintervals:
            count_nonintervals += self[name]
        count_total = count_intervals + count_nonintervals
        if count_total == 0:
            print(f"Intervals: {count_intervals}, Nonintervals: {count_nonintervals}")
        elif count_total != 0:
            print(f"Intervals: {count_intervals}, Nonintervals: {count_nonintervals}, Ratio_of_intervals: {count_intervals/count_total:.2f}")





class DecompositionCollection:
        def __init__(self,*decompositions):
            self.collection=[]
            if decompositions:
                for decomp in decompositions:
                    self.collection.append(decomp)

        def __getitem__(self,item):
            return self.collection[item]

        def __len__(self):
            return len(self.collection)

        def add(self,mult,dim,prime):
            new_decomp=Decomposition(mult,dim,prime)
            self.collection.append(new_decomp)
        
        def dim(self,dim):
            """Return all decompositions that was computed at a given dimension"""
            holder=[]
            for decomp in self.collection:
                if decomp.dim==dim:
                    holder.append(decomp)
            return DecompositionCollection(*holder)
        
        def prime(self,prime):
            holder=[]
            for decomp in self.collection:
                if decomp.prime==prime:
                    holder.append(decomp)
            return DecompositionCollection(*holder)

        def __repr__(self):
            return f'A collection of {len(self.collection)} decompositions @ {object.__repr__(self)}'

        def mult(self,index=None):
            if len(self) == 1:
                return self.collection[0].mult
            else:
                try:
                    return self.collection[index].mult
                except TypeError:
                    return TypeError("Please specify an index.")