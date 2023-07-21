# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 17:29:27 2022

@author: kasumi
"""
import pandas as pd
from ..utils import delete_file
import numpy as np
from bisect import bisect_left
import subprocess, os, sys
#import gc garbage collection
import configparser
import pickle
from warnings import warn
from icecream import ic
from ..utils import filepath_generator
from functools import lru_cache
from .precompute import CommutativeGridPreCompute

#---------Get the path to the binary file of FZZ----------------
# Get the path to the parent directory of this module
parent_dir = os.path.dirname(os.path.abspath(__file__)) + '/../..'
# Initialize the configparser object and read the configuration file
config = configparser.ConfigParser()
config.read(os.path.join(parent_dir, 'config.ini'))

if sys.platform == 'darwin':
    FZZ_BINARY_PATH=config.get('FZZ','binary_path_darwin')
    # try to find the path [PRECOMPUTED] precomputed_intv_directory_darwin
    try:
        PRECOMPUTED_INTV_DIR=config.get('PRECOMPUTED','precomputed_intv_directory_darwin')
    except configparser.NoOptionError:
        PRECOMPUTED_INTV_DIR=''
elif sys.platform == 'linux':
    FZZ_BINARY_PATH=config.get('FZZ','binary_path_linux')
    # try to find the path [PRECOMPUTED] precomputed_intv_directory_linux
    try:
        PRECOMPUTED_INTV_DIR=config.get('PRECOMPUTED','precomputed_intv_directory_linux')
    except configparser.NoOptionError:
        PRECOMPUTED_INTV_DIR=''

#raise warning if the path is not set, say that connected persistence diagram is not available
if FZZ_BINARY_PATH == '':
    warn("The path to the binary file of FZZ is not set. Connected persistence diagram is not available.")


def _fzz_executor(input_file_path, clean_up=True):
    """https://github.com/taohou01/fzz/"""
    # moving files add a little unnecessary overhead
    # but we would like to keep the files well-organized
    # this is fashion is compatible with the multiprocessing mode
    # compared with changing the cwd
    # might need to modify the fzz program directly to 
    # allow the user to specify the directory to store the output file
    input_dir = os.path.abspath(os.path.dirname(input_file_path))
    subprocess.run([FZZ_BINARY_PATH,input_file_path])
    if clean_up:
        delete_file(input_file_path)
    # get the filename of the input file
    input_file_name = os.path.basename(input_file_path)
    # file will be generated in cwd, 
    # with file name being input_file_name removing the extension plus "_pers"
    # get the current directory
    current_dir = os.getcwd()
    fzz_result_fp = os.path.join(current_dir,f"{input_file_name[:-4]}_pers")
    # do not change the line below as the file name is controled by fzz. 
    # if you would like to change it, change the filename of the output first
    target_fp=os.path.join(input_dir,f"{input_file_name[:-4]}_pers")
    # move the file to the input directory
    os.rename(fzz_result_fp,target_fp)
    return target_fp 

        

class ConnectedPersistenceDiagram():
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
                    self.variables = pickle.load(f)
                is_intv_loaded = True
        if not is_intv_loaded:
            temp = CommutativeGridPreCompute(self.m,self.n)
            self.intv = temp.get_intervals()
            self.variables = temp.get_variables()
            del temp
        self.complexes_generator()
        self.node2str_generator()        
        self.path2str_generator()
        self.delt_ss = self.deco()
        self.compute_dec_obj()
        self.compute_connecting_lines()
        self.compute_dotdec()
        self.compute_plot_dots()

    

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

    def temp(self):
        ttt = {'1,1,10,-1': 5,
         '4,4,10,-1': 52,
         '10,-1,0,0': 410,
         '2,3,10,-1': 9,
         '4,5,10,-1': 1,
         '0,0,0,0': 46,
         '1,3,10,-1': 2,
         '2,4,10,-1': 9,
         '4,6,10,-1': 1,
         '0,1,0,0': 1,
         '1,4,10,-1': 11,
         '4,7,10,-1': 1,
         '1,5,10,-1': 1}
        self.dec = ttt

    #@staticmethod
    @lru_cache(maxsize=2048)
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
        self.variables['NodeToStr']=NodeToStr
    
    def path2str_generator(self):
        PathToStr={}  #Dictionary to store string representations of paths 
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
        self.variables['PathToStr']=PathToStr
        # return PathToStr

    def fzz_generator_upper(self):
        # upper layer
        m=self.m
        # n=self.n
        # remove the extension of self.txf and add _FZZ to the filename, use .txt as the extension
        # do not use [:-4], as the length of extension may change
        fzz_input_file_name = filepath_generator(dirname=self.txf_dir,filename=self.txf_basename_wo_ext + '_FZZ_upper',extension='txt')
        with open(fzz_input_file_name, 'w') as f:
            # add the simplices at (0,1) line by line
            f.write(self.variables['NodeToStr'][(0, 1)][0]) 
             # add all simplices from (0,1) to (m-1,1) line by line and by insertion order
            f.write(self.variables['PathToStr'][(0, 1, m-1, 1)][0])
        return _fzz_executor(fzz_input_file_name,clean_up=self.clean_up)
    
    def fzz_generator_lower(self):
        # lower layer
        m=self.m
        # n=self.n
        fzz_input_file_name = filepath_generator(dirname=self.txf_dir,filename=self.txf_basename_wo_ext + '_FZZ_lower',extension='txt')
        with open(fzz_input_file_name, 'w') as f:
            f.write(self.variables['NodeToStr'][(0, 0)][0])
            f.write(self.variables['PathToStr'][(0, 0, m-1, 0)][0])
        return _fzz_executor(fzz_input_file_name,clean_up=self.clean_up)

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
        # self.write_node_to_str(self.variables['NodeToStr'], "NodeToStr.txt")
        # self.write_node_to_str(self.variables['NodeToStr'], "NodeToStr.txt")
        with open(file_path, 'w') as file:
            for key, value in NodeToStr.items():
                file.write(f"{key}: {value[0]}")

    def _barcode_info_transform_ul(self, barcode):
        # for the upper and lower layer
        m=self.m
        dim=self.dim
        for interval in barcode:
            current_dim, p, q = map(int, interval.rstrip().split())
            if current_dim != dim:
                continue
            for j in range(m): 
                if self.variables['S'][j]<p and p<=self.variables['S'][j+1]: 
                    b=j; 
                    break
            for j in range(-1,m): 
                if self.variables['S'][j+1]<=q and q<self.variables['S'][j+2]: 
                    d=j; 
                    break
            if b<=d: 
                self.variables['d_ss'][(b, d)]+=1

    # @staticmethod
    # def fzz_compute_inside_loop(b0,d1,m,NodeToStr,PathToStr,dirname,fn_prefix,clean_up):
    #     fzz_input_file_name = filepath_generator(dirname=dirname,filename=fn_prefix+f'_FZZ_{b0}_{d1}',extension='txt')
    #     with open(fzz_input_file_name, 'w') as f:
    #         f.write(NodeToStr[(0, 1)][0])
    #         if 0<d1:
    #             f.write(PathToStr[(0, 1, d1, 1)][0])
    #         f.write(PathToStr[(d1, 1, b0, 0)][0])
    #         if b0<m-1:
    #             f.write(PathToStr[(b0, 0, m-1, 0)][0])
    #     fzz_output_loop=_fzz_executor(fzz_input_file_name,clean_up=clean_up)
    #     with open(fzz_output_loop, 'r') as f:
    #         barcode = [line.rstrip() for line in f]
    #     if clean_up:
    #         delete_file(fzz_output_loop)
    #     return barcode

    def deco(self):
        #deco for decomposition
        #n = self.n
        m = self.m
        dim = self.dim
        print("全ての道の差分リストを構築")
        self.variables['d_ss'] = {}
        # self.variables['S'] is used to align the index in the commutative ladder
        # with the index when all simplicial complex get expanded and inserted one by one
        # and then computed using fzz
        self.variables['S'] = [0, self.variables['NodeToStr'][(0, 1)][1]] # (0,1), notice the difference
        for i in range(m-1): 
            self.variables['S'].append(self.variables['S'][-1]+self.variables['PathToStr'][(i, 1, i+1, 1)][1])
            # ic(i,self.variables['S'])
        self.variables['S'].append(self.variables['S'][-1]+1)
        # ic(self.variables['S'])
        for i in range(m):
            for j in range(i, m): 
                self.variables['d_ss'][(i, j)]=0

        fzz_output_upper=self.fzz_generator_upper() #initialized with the function
        # notice that S is initialized with S=[0, NodeToStr[(0, 1)][1]] when using this function 
        with open(fzz_output_upper, 'r') as f: # opening the output file of fzz
            barcode = [line.rstrip() for line in f]
        if self.clean_up:
            delete_file(fzz_output_upper)
        # Each line denotes an interval in the barcode, 
        # d p q: dimension, birth, death
        # Note that the birth and death are start and end of the closed integral interval, 
        # i.e., a line d p q indicates a persistence interval [p,q] in dimensional d 
        # starting with the complex K_p and ending with the complex K_q.
        # for i in range(len(barcode)):
        self._barcode_info_transform_ul(barcode)

        e=(m, -1)
        for l in range(m-1, -1, -1):
            for b in range(m-l):
                d=b+l
                self.variables['c_ss'][(e, (b, d))]=self.variables['d_ss'][(b, d)]+self.variables['c_ss'][(e, (b-1, d))]+self.variables['c_ss'][(e, (b, d+1))]-self.variables['c_ss'][(e, (b-1, d+1))]

        self.variables['d_ss']={}
        self.variables['S'] = [0, self.variables['NodeToStr'][(0, 0)][1]] # (0,0), notice the difference
        for i in range(m-1): 
            self.variables['S'].append(self.variables['S'][-1]+self.variables['PathToStr'][(i, 0, i+1, 0)][1])
        self.variables['S'].append(self.variables['S'][-1]+1)
        for i in range(m):
            for j in range(i, m): self.variables['d_ss'][(i, j)]=0

        fzz_output_lower=self.fzz_generator_lower()

        with open(fzz_output_lower, 'r') as f:
            barcode = [line.rstrip() for line in f]
        if self.clean_up:
            delete_file(fzz_output_lower)
        self._barcode_info_transform_ul(barcode)

        for l in range(m-1, -1, -1):
            for b in range(m-l):
                d=b+l
                self.variables['c_ss'][((b, d), e)]=self.variables['d_ss'][(b, d)]+self.variables['c_ss'][((b-1, d), e)]+self.variables['c_ss'][((b, d+1), e)]-self.variables['c_ss'][((b-1, d+1), e)]

        

        non_vanishing_parameters = []
        for b0 in range(m):
            for d1 in range(b0, m):
                if self.variables['c_ss'][((b0, d1), e)]==0 or self.variables['c_ss'][(e, (b0, d1))]==0: 
                    continue
                else:
                    non_vanishing_parameters.append((b0,d1))
        barcodes={}

        NodeToStr=self.variables['NodeToStr']
        PathToStr=self.variables['PathToStr']
        dirname=self.txf_dir
        fn_prefix=self.txf_basename_wo_ext
        clean_up=self.clean_up


        def fzz_compute_inside_loop_local(b0,d1):
            fzz_input_file_name = filepath_generator(dirname=dirname,filename=fn_prefix+f'_FZZ_{b0}_{d1}',extension='txt')
            # it costs little time to write the file
            with open(fzz_input_file_name, 'w') as f:
                f.write(NodeToStr[(0, 1)][0])
                if 0<d1:
                    f.write(PathToStr[(0, 1, d1, 1)][0])
                f.write(PathToStr[(d1, 1, b0, 0)][0])
                if b0<m-1:
                    f.write(PathToStr[(b0, 0, m-1, 0)][0])
            # time-consuming part of this function (99.9%)
            # -----------
            fzz_output_loop=_fzz_executor(fzz_input_file_name,clean_up=clean_up)
            # -----------
            # costs little time to read the file
            try:
                with open(fzz_output_loop, 'r') as f:
                    barcode = [line.rstrip() for line in f]
            except FileNotFoundError:
                #TODO: add a computation failed flag?
                raise FileNotFoundError(f"FileNotFoundError: {fzz_output_loop}")
            if clean_up:
                delete_file(fzz_output_loop)
            return barcode
    
        if not self.enable_multi_processing:
            # NodeToStr=self.variables['NodeToStr']
            # PathToStr=self.variables['PathToStr']
            # Print the progress
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
            
            # Notice that the actual computation is done in a shell script,
            # so for parallelization, we actually need to run multiple shell scripts and let them run in different cores
            # If we only use the vanilla subprocess.run, I believe that the computation is distributed by the OS
            # while the multi-threading here is just start the scripts and them waiting for the result

            #TODO: use async? maybe less overhead, but would be better to setup which core to use
            #TODO: maybe we should set up cpu affinity? or use taskset?
            # https://stackoverflow.com/questions/14716659/taskset-python
            with tqdm_joblib(tqdm(desc="Progress",total=len(non_vanishing_parameters))) as progress_bar:
                results = Parallel(n_jobs=num_cores, timeout=500, prefer='threads')(
                    # delayed(self.fzz_compute_inside_loop)(b0, d1, m=m, \
                    #                                     NodeToStr=self.variables['NodeToStr'],\
                    #                                         PathToStr=self.variables['PathToStr'],\
                    #                                             dirname=self.txf_dir,\
                    #                                                 fn_prefix=self.txf_basename_wo_ext,\
                    #                                                     clean_up=self.clean_up)
                    delayed(fzz_compute_inside_loop_local)(*pair)
                    for pair in non_vanishing_parameters
                )
            

            # cost little time
            for b0, d1 in non_vanishing_parameters:
                barcodes[f"{b0}_{d1}"] = results.pop(0)
                # progress_bar.update(1)   
        
        # measure post-processing time
        from time import time
        # post_processing_start=time()
        # Shape
        # [b1,d1]
        #   [b0,d0]
        # the loop below costs very little time
        for b0 in range(m):
            for d1 in range(b0, m):
                # Recall that e=(m, -1)
                if self.variables['c_ss'][((b0, d1), e)]==0 or self.variables['c_ss'][(e, (b0, d1))]==0: 
                    continue 
                self.variables['d_ss']={}
                self.variables['S']=[0, self.variables['NodeToStr'][(0, 1)][1]]
                for i in range(d1): 
                    self.variables['S'].append(self.variables['S'][-1]+self.variables['PathToStr'][(i, 1, i+1, 1)][1])
                self.variables['S'].append(self.variables['S'][-1]+self.variables['PathToStr'][(d1, 1, b0, 0)][1])
                for i in range(b0, m-1): 
                    self.variables['S'].append(self.variables['S'][-1]+self.variables['PathToStr'][(i, 0, i+1, 0)][1])
                self.variables['S'].append(self.variables['S'][-1]+1)
                for b1 in range(b0+1):
                    for d0 in range(d1, m): 
                        self.variables['d_ss'][((b0, d0), (b1, d1))]=0
                for interval in barcodes[f"{b0}_{d1}"]:
                    current_dim, p, q = map(int, interval.rstrip().split())
                    if current_dim != dim:
                        continue
                    if self.variables['S'][d1+1]<p or q<self.variables['S'][d1+2]: 
                        continue
                    for j in range(d1+1): 
                        if self.variables['S'][j]<p and p<=self.variables['S'][j+1]: 
                            b1=j
                            break
                    for j in range(b0, m): 
                        if self.variables['S'][d1+2+j-b0]<=q and q<self.variables['S'][d1+3+j-b0]: 
                            d0=j
                            break
                    if b1<=d0: 
                        self.variables['d_ss'][(b0, d0), (b1, d1)]+=1
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
                        self.variables['c_ss'][((b0, d0), (b1, d1))]=self.variables['d_ss'][((b0, d0), (b1, d1))]+self.variables['c_ss'][((b0, d0), (b1-1, d1))]+self.variables['c_ss'][((b0, d0+1), (b1, d1))]-self.variables['c_ss'][((b0, d0+1), (b1-1, d1))]      
        

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