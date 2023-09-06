# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 17:29:27 2022

@author: kasumi
"""
import pandas as pd
import numpy as np
from bisect import bisect_left
import os, sys
#import gc garbage collection
import configparser
import pickle
from warnings import warn
from icecream import ic
from functools import lru_cache
from .precompute import CommutativeGridPreCompute
# from ..utils import print_memory_usage_of_all_variables
from pympler import asizeof
from ..utils import CompressedDict
# from fzzpy import compute as zz_compute
# import gc

#TODO:
#TODO string compression for PathToStr and NodeToStr by default
#TODO optional to use a database to store the data
# store the string or torch tensors?


#---------Get the path to the binary file of FZZ----------------
# Get the path to the parent directory of this module
parent_dir = os.path.dirname(os.path.abspath(__file__)) + '/../..'
# Initialize the configparser object and read the configuration file
config = configparser.ConfigParser()
config.read(os.path.join(parent_dir, 'config.ini'))

if sys.platform == 'darwin':
    # try to find the path [PRECOMPUTED] precomputed_intv_directory_darwin
    try:
        PRECOMPUTED_INTV_DIR=config.get('PRECOMPUTED','precomputed_intv_directory_darwin')
    except configparser.NoOptionError:
        PRECOMPUTED_INTV_DIR=''
elif sys.platform == 'linux':
    # try to find the path [PRECOMPUTED] precomputed_intv_directory_linux
    try:
        PRECOMPUTED_INTV_DIR=config.get('PRECOMPUTED','precomputed_intv_directory_linux')
    except configparser.NoOptionError:
        PRECOMPUTED_INTV_DIR=''
        

class ConnectedPersistenceDiagram():
    __slots__ = ['txf','txf_dir','txf_basename_wo_ext','m','ladder_length',\
                 'enable_multi_processing','num_cores','clean_up','n','dim',\
                    'times','intv','variables','complexes','delt_ss','d_ss','dec',\
                        'indexAligner','dots','lines','dotdec','plot_dots',\
                            'NodeToStr','PathToStr']

    def __init__(self, filtration_filepath,ladder_length,homology_dim,filtration_values,enable_multi_processing=False,num_cores="auto",clean_up=True,**kwargs ):
        self.txf = os.path.abspath(filtration_filepath) # filtration file
        #TODO: validate the txf file, check if all faces are contained, etc. But validation costs time. do we really need to do that?
        self.txf_dir = os.path.dirname(self.txf)
        self.txf_basename_wo_ext = os.path.splitext(os.path.basename(self.txf))[0]
        self.m = ladder_length # default length is 10
        self.ladder_length = self.m
        self.enable_multi_processing = enable_multi_processing
        self.num_cores = num_cores
        self.clean_up = clean_up # clean up the temporary files
        self.n = 2 # two layers by default
        self.dim = homology_dim # homology dimension
        self.times = self.preprocess_filtration_values(filtration_values)

        is_intv_loaded = False
        if PRECOMPUTED_INTV_DIR:
            intv_fn=f"{PRECOMPUTED_INTV_DIR}/intv_{self.m:03d}_{self.n:03d}.pkl"
            variables_fn=f"{PRECOMPUTED_INTV_DIR}/variables_{self.m:03d}_{self.n:03d}.pkl"
            if os.path.exists(intv_fn) and os.path.exists(variables_fn):
                print("Loading precomputed intervals and variables...")
                with open(intv_fn,"rb") as f:
                    self.intv = pickle.load(f)
                with open(variables_fn,"rb") as f:
                    self.variables = pickle.load(f) # get 'cov' and 'c_ss'
                is_intv_loaded = True
        if not is_intv_loaded:
            temp = CommutativeGridPreCompute(self.m,self.n)
            self.intv = temp.get_intervals()
            self.variables = temp.get_variables() # get 'cov' and 'c_ss'
            del temp
        # print("Preloading/precomputing complete!")
        self.complexes_generator()
        self.NodeToStr = self.node2str_generator()        
        self.PathToStr = self.path2str_generator()
        del self.complexes
        self.delt_ss = self.deco()
        self.compute_dec_obj()
        self.compute_connecting_lines()
        self.compute_dotdec()
        self.compute_plot_dots()

    # def __del__(self):
    #     self.variables.clear()
    #     self.intv.clear()
    #     self.delt_ss.clear()
    #     self.complexes.clear()
    #     self.S = []
    #     gc.collect()
    #     print("Destructor called, ConnectedPersistenceDiagram deleted.")

    def preprocess_filtration_values(self,filtration_values):
        """Preprocess the filtration values"""
        if len(filtration_values) != self.m:
            raise ValueError("The length of the filtration value list is not equal to the ladder length.")
        # raise error if not sorted strictly increasing
        if not all(filtration_values[i] < filtration_values[i+1] for i in range(len(filtration_values)-1)):
            raise ValueError("The filtration values provided are not strictly increasing.")
        return np.asarray(filtration_values)

    @property
    def plot_data(self):
        plot_data_dict = {}
        plot_data_dict.update({'ladder_length': self.ladder_length})
        plot_data_dict.update({'dim': self.dim})
        plot_data_dict.update({'radii': self.times})
        plot_data_dict.update({'dots': self.dots.to_csv(index=True)})
        plot_data_dict.update({'lines': self.lines.to_csv(index=True)})
        return plot_data_dict


    #@staticmethod
    @lru_cache(maxsize=4096)
    def join_intv(self, X, Y):
        """
        helper function to join two intervals
        works for 2D commutative grid
        """
        n = self.n # number of layers (rows), will be two for commutative ladders
        # n will be the length of both X and Y 
        Z = list(X)
        for j in range(n):
            Z[j] = (min(X[j][0], Y[j][0]), max(X[j][1], Y[j][1]))
        for s in range(n):
            if Z[s][1] > -1: break
        for t in range(n-1, -1, -1):
            if Z[t][1] > -1: break
        if s < t and Z[s][1] < Z[s+1][1]:
            Z[s] = (Z[s][0], Z[s][1]+1)
        if s < t and Z[t][0] > Z[t-1][0]:
            Z[t] = (Z[t][0]-1, Z[t][1])
        return tuple(Z)
    
    def complexes_generator(self):
        """compute complexes based on the time parameter in the filtration file"""
        # C[i][j], i in range(m), j in range(n)
        # i: time index
        # j: layer index
        C = [[set() for j in range(self.n)] for i in range(self.m)]
        # C is a list of lists of sets, 
        # each set contains strings of vertices, 
        # each string represents a simplex
        with open(self.txf, 'r') as f:
            filt = [line.rstrip() for line in f]
            # line is in form of
            # dim birth n m v_0...v_dim
            # filt=f.read().rstrip().split('\n') #filtration
        if filt[0] == '':
            return
        for i in range(len(filt)):
            data=filt[i].rstrip().split()
            # data = filt[i].split()
            if data[0] == '#': continue # skip comments
            if self.dim + 1 < int(data[0]): continue # skip higher dimensions
            cur_time = float(data[1])
            y_index = int(data[2])
            # x_index should be determined by cur_time and self.times
            x_index = bisect_left(self.times, cur_time)
            if x_index == len(self.times): #skip if cur_time is larger than the largest time in the filtration
                break
            # data[3]: horizontal index
            # data[2]: vertical index
            # C[x_index][y_index].add(' '.join(sorted(data[4:])))
            # check if sorted here is sufficient, or if it is necessary to sort
            # I believe that it works well as long as it is sorted, no matter the order'
            # maybe better to change it to the one below
            C[x_index][y_index].add(' '.join(sorted(data[4:], key=lambda x: (len(x), x))))
        # up to now, C contains each simplices newly added at each step.
        for i in range(1, self.m): # Reconstruct the lower layer
            C[i][0] = C[i][0] | C[i-1][0] # union
        for j in range(1, self.n): # reconstruct the leftest column
            # for self.n=2, we only need to reconstruct the first column
            C[0][j] = C[0][j] | C[0][j-1]
        # Reconstruction of the upper layer staring from the second column
        for i in range(1, self.m):
            for j in range(1, self.n):
                C[i][j] = C[i][j] | C[i-1][j] | C[i][j-1]

        self.complexes = C


    def node2str_generator(self):
        NodeToStr={} #Dictionary to store string representations of nodes
        # format for each value: simplex, length of simplex (i.e., number of vertices)
        m=self.m
        n=self.n
        s=''
        #raise error if self.complexes is not defined
        if not hasattr(self, 'complexes'):
            raise AttributeError("self.complexes is not defined. Please run self.complexes_generator() first.")       
        C=self.complexes
        for a in range(m):
            for b in range(n):
                L=list(C[a][b])
                if len(L)==0: #TODO: check correctness
                    NodeToStr[(a, b)]=('', 0)
                    continue
                L.sort(key=lambda x: (len(x.split(' ')),tuple(map(int,x.split(' ')))))  
                s='\ni '.join(L) 
                NodeToStr[(a, b)]=('i '+s+'\n', len(L))

        if self.enable_multi_processing:
            from multiprocessing import Manager
            # return Manager().dict(NodeToStr)
            # return NodeToStr
            return Manager().dict(NodeToStr)
        else:
            return NodeToStr
    
    def path2str_generator(self):
        PathToStr=CompressedDict()  #Compressed Dictionary to store string representations of paths 
        m=self.m
        n=self.n
        s=''
        if not hasattr(self, 'complexes'):
            raise AttributeError("self.complexes is not defined. Please run self.complexes_generator() first.")       
        C=self.complexes
        for a in range(m):
            L=list(C[a][1]-C[a][0]); 
            L.sort(key=lambda x: (len(x.split(' ')),tuple(map(int,x.split(' ')))))  
            if len(L)<1: 
                PathToStr[(a, 0, a, 1)]=('', 0)
                PathToStr[(a, 1, a, 0)]=('', 0)
                continue
            s='\ni '.join(L) 
            PathToStr[(a, 0, a, 1)]=('i '+s+'\n', len(L))
            L.reverse() 
            s='\nd '.join(L) 
            PathToStr[(a, 1, a, 0)]=('d '+s+'\n', len(L))
        
        for a in range(m-1):
            for b in range(n):
                L=list(C[a+1][b]-C[a][b]); 
                L.sort(key=lambda x: (len(x.split(' ')),tuple(map(int,x.split(' ')))))  
                if len(L)<1: 
                    PathToStr[(a, b, a+1, b)]=('', 0)
                    PathToStr[(a+1, b, a, b)]=('', 0)
                    continue
                s='\ni '.join(L)
                PathToStr[(a, b, a+1, b)]=('i '+s+'\n', len(L))
                L.reverse() 
                s='\nd '.join(L) 
                PathToStr[(a+1, b, a, b)]=('d '+s+'\n', len(L))
            PathToStr[(a, 0, a+1, 1)]=(PathToStr[(a, 0, a+1, 0)][0]+PathToStr[(a+1, 0, a+1, 1)][0], PathToStr[(a, 0, a+1, 0)][1]+PathToStr[(a+1, 0, a+1, 1)][1])
            PathToStr[(a+1, 1, a, 0)]=(PathToStr[(a+1, 1, a, 1)][0]+PathToStr[(a, 1, a, 0)][0], PathToStr[(a+1, 1, a, 1)][1]+PathToStr[(a, 1, a, 0)][1])
        
        for l in range(2, m):
            a=0
            while a+l<m:
                for b in range(n):
                    PathToStr[(a, b, a+l, b)]=(PathToStr[(a, b, a+l-1, b)][0]+PathToStr[(a+l-1, b, a+l, b)][0], PathToStr[(a, b, a+l-1, b)][1]+PathToStr[(a+l-1, b, a+l, b)][1])
                    PathToStr[(a+l, b, a, b)]=(PathToStr[(a+l, b, a+1, b)][0]+PathToStr[(a+1, b, a, b)][0], PathToStr[(a+l, b, a+1, b)][1]+PathToStr[(a+1, b, a, b)][1])
                PathToStr[(a, 0, a+l, 1)]=(PathToStr[(a, 0, a+l, 0)][0]+PathToStr[(a+l, 0, a+l, 1)][0], PathToStr[(a, 0, a+l, 0)][1]+PathToStr[(a+l, 0, a+l, 1)][1])
                PathToStr[(a+l, 1, a, 0)]=(PathToStr[(a+l, 1, a, 1)][0]+PathToStr[(a, 1, a, 0)][0], PathToStr[(a+l, 1, a, 1)][1]+PathToStr[(a, 1, a, 0)][1])
                a+=1
        if self.enable_multi_processing:
            from commutazzio.utils import CompressedDictManager
            manager = CompressedDictManager()
            manager.start()
            return manager.CompressedDict(PathToStr)
        else:
            return PathToStr

    @staticmethod
    def _data_source_to_filts(data_source):
        filt_simps = []
        filt_ops = []
        if data_source:
            for data in data_source:
                lines = data.strip().split("\n")
                for line in lines:
                    parts = line.split()
                    try:
                        op = parts[0]
                    except IndexError:
                        # print everything
                        print(f"data_source: {data_source}")
                        print(f"line: {line}")
                        print(f"parts: {parts}")
                        breakpoint()
                        1+1
                    simp = list(map(int, parts[1:]))
                    filt_simps.append(simp)
                    if op == "i":
                        filt_ops.append(True)
                    elif op == "d":
                        filt_ops.append(False)
        return filt_simps, filt_ops

    def fzz_barcode_compute_upper(self):
        from fzzpy import compute as zz_compute
        # upper layer
        m=self.m
        # n=self.n
        # Consolidate data source
        data_source = [
            self.NodeToStr[(0, 1)][0],
            self.PathToStr[(0, 1, m-1, 1)][0]
        ]
        filt_simps, filt_ops = self._data_source_to_filts(data_source)
        # write data_source to file with random filename 
        # from uuid import uuid4
        # filename = uuid4().hex[-6:]
        # with open(f"data_source_{filename}.txt", 'w') as file:
        #     for data in data_source:
        #         file.write(data)
        # print("Writing data sources to file complete.")
        del data_source
        print("Computing upper layer barcode...")
        barcode = zz_compute(filt_simps,filt_ops)
        del filt_simps, filt_ops
        return barcode
    
    def fzz_barcode_compute_lower(self):
        from fzzpy import compute as zz_compute
        # lower layer
        m=self.m
        # n=self.n
        filt_simps = []
        filt_ops = []
        # Consolidate data sources
        data_source = [
            self.NodeToStr[(0, 0)][0],
            self.PathToStr[(0, 0, m-1, 0)][0]
        ]
        filt_simps, filt_ops = self._data_source_to_filts(data_source)
        del data_source
        barcode = zz_compute(filt_simps,filt_ops)
        del filt_simps, filt_ops
        return barcode
    
    @staticmethod
    def fzz_compute_inside_loop_local_mp(args):
        from fzzpy import compute as zz_compute
        b0, d1,m, NodeToStr, PathToStr  = args
        # Generate data directly
        data_source = [NodeToStr[(0, 1)][0]]
        if 0 < d1:
            data_source.append(PathToStr[(0, 1, d1, 1)][0])
        data_source.append(PathToStr[(d1, 1, b0, 0)][0])
        if b0 < m-1:
            data_source.append(PathToStr[(b0, 0, m-1, 0)][0])
        # Parse the data source directly to generate filt_simp and filt_op
        filt_simps, filt_ops = ConnectedPersistenceDiagram._data_source_to_filts(data_source)
        # Compute using the directly generated data
        barcode = zz_compute(filt_simps, filt_ops)
        return barcode

    @staticmethod
    def write_list_of_lists_of_sets_to_file(file_path, list_of_lists_of_sets):
        with open(file_path, 'w') as file:
            for list_of_sets in list_of_lists_of_sets:
                for index, s in enumerate(list_of_sets):
                    sorted_set = sorted(s)
                    if index == len(list_of_sets) - 1:
                        file.write(f"{sorted_set}\n")
                    else:
                        file.write(f"{sorted_set}, ")

    @staticmethod
    def write_node_to_str(NodeToStr, file_path):
        # self.write_node_to_str(self.NodeToStr, "NodeToStr.txt")
        # self.write_node_to_str(self.NodeToStr, "NodeToStr.txt")
        with open(file_path, 'w') as file:
            for key, value in NodeToStr.items():
                file.write(f"{key}: {value[0]}")

    def _barcode_info_transform_ul(self, barcode):
        # for the upper and lower layer
        m=self.m
        dim=self.dim
        for interval in barcode:
            current_dim, p, q = interval #map(int, interval.rstrip().split())
            if current_dim != dim:
                continue
            for j in range(m): 
                if self.indexAligner[j]<p and p<=self.indexAligner[j+1]: 
                    b=j; 
                    break
            for j in range(-1,m): 
                if self.indexAligner[j+1]<=q and q<self.indexAligner[j+2]: 
                    d=j; 
                    break
            if b<=d: 
                self.d_ss[(b, d)]+=1


    def print_memory_usage_of_attributes(obj):
        for slot in obj.__slots__:
            value = getattr(obj, slot, None)  # Get the value of the slot/attribute
            if value is not None:
                # Check if it's a managed object
                if hasattr(value, '_getvalue') and 'Proxy' in value.__class__.__name__:
                    serialized_value = pickle.dumps(value._getvalue())
                    memory_usage = asizeof.asizeof(serialized_value) / (1024 * 1024)  # Convert to MB
                    del serialized_value
                else:
                    memory_usage = asizeof.asizeof(value) / (1024 * 1024)  # Convert to MB (this will error here since we don't have pympler)
                print(f"Memory usage of attribute '{slot}': {memory_usage:.2f} MB")


    def deco(self):
        # import pdb
        # pdb.set_trace()
        # breakpoint()
        #deco for decomposition
        #n = self.n
        m = self.m
        dim = self.dim
        # print("全ての道の差分リストを構築")
        print("Building the difference list of all paths...")
        self.d_ss = {}
        # self.indexAligner is used to align the index in the commutative ladder
        # with the index when all simplicial complex get expanded and inserted one by one
        # and then computed using fzz
        self.indexAligner = [0, self.NodeToStr[(0, 1)][1]] 
        # (0,1), notice the difference
        for i in range(m-1): 
            self.indexAligner.append(self.indexAligner[-1]+self.PathToStr[(i, 1, i+1, 1)][1])
            # ic(i,self.indexAligner)
        self.indexAligner.append(self.indexAligner[-1]+1)
        # ic(self.indexAligner)
        for i in range(m):
            for j in range(i, m): 
                self.d_ss[(i, j)]=0
        print("Difference list building complete.")

        
        self.print_memory_usage_of_attributes()

        # Each line denotes an interval in the barcode, 
        # d p q: dimension, birth, death
        # Note that the birth and death are start and end of the closed integral interval, 
        # i.e., a line d p q indicates a persistence interval [p,q] in dimensional d 
        # starting with the complex K_p and ending with the complex K_q.
        # for i in range(len(barcode)):     
        #-----------------start of upper layer-----------------
        # notice that S is initialized with S=[0, NodeToStr[(0, 1)][1]] when using this function 
        barcode = self.fzz_barcode_compute_upper()
        self._barcode_info_transform_ul(barcode) # change the indexing
        print("Upper layer barcode computation complete!")
        #-----------------end of upper layer-----------------

        e=(m, -1)
        for l in range(m-1, -1, -1):
            for b in range(m-l):
                d=b+l
                self.variables['c_ss'][(e, (b, d))]=self.d_ss[(b, d)]+self.variables['c_ss'][(e, (b-1, d))]+self.variables['c_ss'][(e, (b, d+1))]-self.variables['c_ss'][(e, (b-1, d+1))]

        self.d_ss={}
        self.indexAligner = [0, self.NodeToStr[(0, 0)][1]] 
        # (0,0), notice the difference
        for i in range(m-1): 
            self.indexAligner.append(self.indexAligner[-1]+self.PathToStr[(i, 0, i+1, 0)][1])
        self.indexAligner.append(self.indexAligner[-1]+1)
        for i in range(m):
            for j in range(i, m): 
                self.d_ss[(i, j)]=0

        #-----------------start of lower layer-----------------
        barcode = self.fzz_barcode_compute_lower()
        self._barcode_info_transform_ul(barcode)
        print("Lower layer barcode computation complete!")
        #-----------------end of lower layer-----------------

        for l in range(m-1, -1, -1):
            for b in range(m-l):
                d=b+l
                self.variables['c_ss'][((b, d), e)]=self.d_ss[(b, d)]+self.variables['c_ss'][((b-1, d), e)]+self.variables['c_ss'][((b, d+1), e)]-self.variables['c_ss'][((b-1, d+1), e)]

        

        non_vanishing_parameters = []
        for b0 in range(m):
            for d1 in range(b0, m):
                if self.variables['c_ss'][((b0, d1), e)]==0 or self.variables['c_ss'][(e, (b0, d1))]==0: 
                    continue
                else:
                    non_vanishing_parameters.append((b0,d1))
        barcodes={}

        # def fzz_compute_inside_loop_local(b0, d1,NodeToStr=self.NodeToStr,PathToStr=self.PathToStr):
        # # def fzz_compute_inside_loop_local(b0, d1):
        #     print(f"Subprocess - NodeToStr ID: {id(NodeToStr)}")
        #     print(f"Subprocess - PathToStr ID: {id(PathToStr)}")            

    
        if not self.enable_multi_processing:
            NodeToStr=self.NodeToStr
            PathToStr=self.PathToStr
            # Print the progress
            def fzz_compute_inside_loop_local(b0, d1):
                from fzzpy import compute as zz_compute
                # Generate data directly
                data_source = [NodeToStr[(0, 1)][0]]
                if 0 < d1:
                    data_source.append(PathToStr[(0, 1, d1, 1)][0])
                data_source.append(PathToStr[(d1, 1, b0, 0)][0])
                if b0 < m-1:
                    data_source.append(PathToStr[(b0, 0, m-1, 0)][0])
                # Parse the data source directly to generate filt_simp and filt_op
                filt_simps, filt_ops = self._data_source_to_filts(data_source)
                del data_source
                # Compute using the directly generated data
                barcode = zz_compute(filt_simps, filt_ops)
                return barcode
            progress_count=0
            for b0,d1 in non_vanishing_parameters:
                # barcodes[f"{b0}_{d1}"] = self.fzz_compute_inside_loop(b0,d1,m=m,\
                #                                                           NodeToStr=None,PathToStr=None,\
                #                                                             dirname=self.txf_dir,\
                #                                                             fn_prefix=self.txf_basename_wo_ext,\
                #                                                             clean_up=self.clean_up)
                barcodes[f"{b0}_{d1}"] = fzz_compute_inside_loop_local(b0,d1)
                progress_count+=1
                print('\rProgress: {0:.2f}％ '.format(100*progress_count/len(non_vanishing_parameters)), end='')
        else:
            # Parallelize the loop
            from os import cpu_count
            from tqdm import tqdm
            from ..utils import tqdm_joblib
            from joblib import delayed, Parallel  
            self.print_memory_usage_of_attributes()
            max_cores=cpu_count() 
            num_cores=self.num_cores
            if num_cores == "auto":       
                num_cores = max(1,max_cores-2)
            elif self.num_cores > max_cores:
                print(f"Number of cores specified ({num_cores}) is larger than the maximum number of cores ({max_cores}).")
                print(f"Resetting number of cores to {max_cores}.")
                num_cores=max_cores
            print('Number of cores being used:',num_cores)
            print(f"Number of non-vanishing parameters: {len(non_vanishing_parameters)}")
            from multiprocessing import Pool
            self.print_memory_usage_of_attributes()
            args_list = [(b0, d1, self.m, self.NodeToStr, self.PathToStr) for b0, d1 in non_vanishing_parameters]
            # Use Pool for parallel processing
            with Pool(processes=num_cores) as pool:
                results = list(\
                    tqdm(\
                        pool.imap_unordered(self.fzz_compute_inside_loop_local_mp,args_list),
                                    total=len(non_vanishing_parameters), desc="Progress"))
                
            # cost little time
            for b0, d1 in non_vanishing_parameters:
                barcodes[f"{b0}_{d1}"] = results.pop(0)
                # progress_bar.update(1)   
            # del results
            # gc.collect()
        
        # the loop below costs very little time
        for b0 in range(m):
            for d1 in range(b0, m):
                # Recall that e=(m, -1)
                if self.variables['c_ss'][((b0, d1), e)]==0 or self.variables['c_ss'][(e, (b0, d1))]==0: 
                    continue 
                self.d_ss={}
                self.indexAligner=[0, self.NodeToStr[(0, 1)][1]]
                for i in range(d1): 
                    self.indexAligner.append(self.indexAligner[-1]+self.PathToStr[(i, 1, i+1, 1)][1])
                self.indexAligner.append(self.indexAligner[-1]+self.PathToStr[(d1, 1, b0, 0)][1])
                for i in range(b0, m-1): 
                    self.indexAligner.append(self.indexAligner[-1]+self.PathToStr[(i, 0, i+1, 0)][1])
                self.indexAligner.append(self.indexAligner[-1]+1)
                for b1 in range(b0+1):
                    for d0 in range(d1, m): 
                        self.d_ss[((b0, d0), (b1, d1))]=0
                for interval in barcodes[f"{b0}_{d1}"]:
                    current_dim, p, q = interval #map(int, interval.rstrip().split())
                    if current_dim != dim:
                        continue
                    if self.indexAligner[d1+1]<p or q<self.indexAligner[d1+2]: 
                        continue
                    for j in range(d1+1): 
                        if self.indexAligner[j]<p and p<=self.indexAligner[j+1]: 
                            b1=j
                            break
                    for j in range(b0, m): 
                        if self.indexAligner[d1+2+j-b0]<=q and q<self.indexAligner[d1+3+j-b0]: 
                            d0=j
                            break
                    if b1<=d0: 
                        self.d_ss[(b0, d0), (b1, d1)]+=1
                self.variables['c_ss'][((b0, m), (-1, d1))]=0
                for i in range(d1, m): 
                    self.variables['c_ss'][((b0, i), (-1, d1))]=0
                for i in range(b0+1): 
                    self.variables['c_ss'][((b0, m), (i, d1))]=0
                for l in range(m-1, d1-b0-1, -1):
                    for b1 in range(m-l):
                        if b0<b1: 
                            break
                        d0=b1+l
                        if d0<d1 or m-1<d0: 
                            continue
                        self.variables['c_ss'][((b0, d0), (b1, d1))]=self.d_ss[((b0, d0), (b1, d1))]+self.variables['c_ss'][((b0, d0), (b1-1, d1))]+self.variables['c_ss'][((b0, d0+1), (b1, d1))]-self.variables['c_ss'][((b0, d0+1), (b1-1, d1))]      
        

        # last info
        print("仕上がり中..")
        delt_ss={}

        for I in self.intv:
            t = len(self.variables['cov'][I]); 
            subs = 1 << t
            ans_ss = 0
            for s in range(subs):
                js = I
                sl = 0
                for j in range(t):
                    if (1 << j) & s:
                        sl += 1
                        js = self.join_intv(js, self.variables['cov'][I][j])
                # remove the usage of (-1)^sl
                # ans_ss += ((-1)**sl)*self.variables['c_ss'][js]
                if sl%2==0:
                    ans_ss += self.variables['c_ss'][js]
                else:
                    ans_ss -= self.variables['c_ss'][js]
            delt_ss[I] = ans_ss
        # post_processing_end=time()
        # print post-processing time in seconds
        # print(f"post-processing time: {post_processing_end-post_processing_start} seconds")
        return delt_ss

    def compute_dec_obj(self):
        if not hasattr(self, 'delt_ss'):
            raise ValueError('delt_ss not computed yet.')
        dec = {}
        for I in self.intv:
            if self.delt_ss[I] != 0:
                S = f"{I[0][0]},{I[0][1]},{I[1][0]},{I[1][1]}"
                dec[S] = self.delt_ss[I]
        self.dec = dec

    def wake(self, I):
        # for 分ける
        # do not need to use cache as for each I only called once
        m = self.m
        K = I.split(',')
        return [f"{K[0]},{K[1]},{m},-1", f"{m},-1,{K[2]},{K[3]}"]

    def compute_dotdec(self):
        '''Generate decomposition for dots
        '''
        m = self.m
        dotdec = {}  # empty dict
        dotdec[f"{m},-1,{m},-1"] = 0
        for i in range(m):
            for j in range(i, m):
                dotdec[f"{i},{j},{m},-1"] = 0
                dotdec[f"{m},-1,{i},{j}"] = 0
        for I in self.dec:
            J = self.wake(I)
            dotdec[J[0]] += self.dec[I]
            dotdec[J[1]] += self.dec[I]
        self.dotdec = dotdec

    def compute_connecting_lines(self):
        if not hasattr(self, 'dec'):
            raise ValueError('decomposition not computed yet.')
        m = self.m
        # initiate a pandas dataframe with specified types
        container = pd.DataFrame(
            {'x0': pd.Series(dtype='int'),
             'y0': pd.Series(dtype='int'),
             'x1': pd.Series(dtype='int'),
             'y1': pd.Series(dtype='int'),
             'multiplicity': pd.Series(dtype='int')
             })
             # (x0,y0) bottom right; (x1,y1) top left
        for I in self.dec:
            (b1, d1, b2, d2)=map(lambda x: int(x)+1, I.split(','))
            if(d1 <= 0 or d2 <= 0 or (b1 == d1 and b2 == d2)):
                continue
            slope = (d2-b1)/(d1-b2)
            if slope <= 1:
                # notice that the y-coordinate in html canvas is inverted
                container.loc[len(container)]= [d1, b1, b2, d2, self.dec[I]]
        self.lines= container

    def compute_plot_dots(self):
        if not hasattr(self, 'dotdec'):
            raise ValueError('dot decomposition not computed yet.')
        m= self.m
        # initiate a pandas dataframe with specified types
        container = pd.DataFrame(
            {'x': pd.Series(dtype='int'),
             'y': pd.Series(dtype='int'),
             'multiplicity': pd.Series(dtype='int'),
             'area': pd.Series(dtype='str')
             })
        for i in range(m):
            for j in range(i, m):
                D= self.dotdec[f"{i},{j},{m},-1"]
                U= self.dotdec[f"{m},-1,{i},{j}"]
                if D != 0:
                    container.loc[len(container)] = [j+1, i+1, D, 'D',] 
                if U != 0:
                    container.loc[len(container)] = [i+1, j+1, U, 'U',]
        self.dots= container