#from collections import namedtuple
import numpy as np


cl4_equi_intervals=[f"I{i}" for i in range(1,56)]
cl4_equi_nonintervals=[f"N{i}" for i in range(1,22)]
cl4_equi_isoclasses=cl4_equi_nonintervals + cl4_equi_intervals
#cl4_equi_isoclasses=[f"N{i}" for i in range(1,22)]+[f"I{i}" for i in range(1,56)]

#multi_vec_cl4_equi=namedtuple('cl4_equi',cl4_equi_isoclasses)


class multiplicities:
    """A namedtuple-like class to store information of multiplicity values."""
    def __init__(self,array,dim,prime):
        #self._array = multi_vec_cl4_equi(*array.flatten())
        self._array = {k:v for k,v in zip(cl4_equi_isoclasses,array.flatten())}
        self._dim = dim
        self._prime = prime

    def __getitem__(self,item):
        return self._array[item]

    @property
    def array(self):
        return self._array

    @property
    def dim(self):
        return self._dim
    
    @property
    def prime(self):
        return self._prime

    def pretty_print(self):
        """Print out the multiplicity values line by line"""
        for k,v in self._array.items():
            print(f"{k}:{v}")

    def __repr__(self):
        return f"array: {str(self.array)},\ndim: {str(self.dim)},\nprime: {str(self.prime)}"

    def nonzero_nonintervals(self):
        """Return non-trivial non-intervals"""
        return {k:v for (k,v) in self.array.items() if v!=0 and k[0]=='N'}

        

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
            print(f"Intervals: {count_intervals}, Nonintervals: {count_nonintervals}, Ratio: {count_intervals/count_total:.2f}")





class MultiplicityVectors:
        def __init__(self,*multis):
            self.vectors=[]
            if multis:
                for m in multis:
                    self.vectors.append(m)

        def __getitem__(self,item):
            return self.vectors[item]

        def __len__(self):
            return len(self.vectors)

        def add(self,vector,dim,prime):
            new_vector=multiplicities(vector,dim,prime)
            self.vectors.append(new_vector)
        
        def dim(self,dim):
            dim_vectors=[]
            for vector in self.vectors:
                if vector.dim==dim:
                    dim_vectors.append(vector)
            return MultiplicityVectors(*dim_vectors)
        def prime(self,prime):
            prime_vectors=[]
            for vector in self.vectors:
                if vector.prime==prime:
                    prime_vectors.append(vector)
            return MultiplicityVectors(*prime_vectors)

        def __repr__(self):
            description=f'A collection of {len(self.vectors)} multiplicity vector(s).'
            return description

        def array(self,index=None):
            if len(self) == 1:
                return self.vectors[0].array
            else:
                try:
                    return self.vectors[index].array
                except TypeError:
                    return TypeError("Please specify an index.")



if __name__ == '__main__':
    holder=MultiplicityVectors()
    test=np.arange(76)
    holder.add(test,2,3)