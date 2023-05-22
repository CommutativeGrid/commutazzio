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
from warnings import warn
from icecream import ic
from ..utils import filepath_generator

#---------Get the path to the binary file of FZZ----------------
# Get the path to the parent directory of this module
parent_dir = os.path.dirname(os.path.abspath(__file__)) + '/../..'
# Initialize the configparser object and read the configuration file
config = configparser.ConfigParser()
config.read(os.path.join(parent_dir, 'config.ini'))

if sys.platform == 'darwin':
    FZZ_BINARY_PATH=config.get('FZZ','binary_path_darwin')
elif sys.platform == 'linux':
    FZZ_BINARY_PATH=config.get('FZZ','binary_path_linux')

#raise warning if the path is not set, say that connected persistence diagram is not available
if FZZ_BINARY_PATH == '':
    warn("The path to the binary file of FZZ is not set. Connected persistence diagram is not available.")


#-----------------End of getting the path----------------------

# def toList(st):
#     return list(map(int, st.split(',')))

class ConnectedPersistenceDiagram():
    def __init__(self, filtration_filepath,ladder_length,homological_dim,filtration_values,clean_up=True,**kwargs ):
        self.txf = os.path.abspath(filtration_filepath) # filtration file
        self.txf_dir = os.path.dirname(self.txf)
        self.txf_basename_wo_ext = os.path.splitext(os.path.basename(self.txf))[0]
        self.m = ladder_length # default length is 10
        self.ladder_length = self.m
        self.clean_up = clean_up # clean up the temporary files
        self.n = 2 # two layers by default
        self.dim = homological_dim # homological dimension
        self.times = self.preprocess_filtration_values(filtration_values)
        self.intv = self.interval_generator()
        self.variables={'cov':{},'c_ss':{}}
        # c_ss stands for compression source-sink 
        self.cover_generator()
        self.delt_ss = self.deco()
        self.compute_dec_obj()
        self.compute_connecting_lines()
        self.compute_dotdec()
        self.compute_plot_dots()

    #TODO: validate the txf file
    #TODO: check if all faces are contained, etc.

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

    def interval_generator(self):
        """Generate intervals"""
        n = self.n  # vertical height, use !n in debug mode
        m = self.m  # horizontal length, 2 by default
        intv = []
        for k in range(n):
            for birth in range(m):
                for death in range(birth, m):
                    I = [(m, -1) for _ in range(k)]
                    I.append((birth, death))
                    intv.append(I)
        i = 0
        while(i < len(intv)):
            I = intv[i]
            if len(I) < n:
                p, q = I[-1]
                for b in range(p+1):
                    for d in range(p, q+1):
                        intv.append(I+[(b, d)])
            I.extend([(m, -1) for j in range(n-len(I))])
            intv[i] = tuple(I)
            i += 1
        # intv.sort(key=self.sizeSupp)
        print(f"全{str(len(intv))}個の区間表現を構築")
        # self.intv=intv
        return intv

    def cover_generator(self):
        """generate interval covers"""
        cov = {}
        n = self.n
        m = self.m
        for I in self.intv:
            self.variables['c_ss'][I]=0
            for s in range(n):
                if I[s][1] > -1:
                    break
            for t in range(n-1, -1, -1):
                if I[t][1] > -1:
                    break
            cov[I] = []  # cover
            b = I[t][0]  # birth
            d = I[s][1]  # death
            if t < n-1:
                L = list(I); L[t+1] = (b, b)
                cov[I].append(tuple(L))
            if s > 0:
                L = list(I); L[s-1] = (d, d)
                cov[I].append(tuple(L))
            if b > 0:
                L = list(I); L[t] = (b-1, I[t][1])
                cov[I].append(tuple(L))
            for j in range(t-1, s-1, -1):
                if I[j+1][0] < I[j][0]:
                    L = list(I); L[j] = (I[j][0]-1, I[j][1])
                    cov[I].append(tuple(L))
            if d < m-1:
                L = list(I); L[s] = (I[s][0], d+1)
                cov[I].append(tuple(L))
            for j in range(s+1, t+1):
                if I[j-1][1] > I[j][1]:
                    L = list(I); L[j] = (I[j][0], I[j][1]+1)
                    cov[I].append(tuple(L))
        self.variables['cov']=cov
        # return cov


    #@staticmethod
    def join_intv(self, X, Y):
        """helper function to join two intervals"""
        n = self.n
        Z = list(X)
        for j in range(n):
            Z[j] = (min(X[j][0], Y[j][0]), max(X[j][1], Y[j][1]))
        for s in range(n):
            if Z[s][1] > -1: break
        for t in range(n-1, -1, -1):
            if Z[t][1] > -1: break
        if s < t and Z[s][1] < Z[s+1][1]: Z[s] = (Z[s][0], Z[s][1]+1)
        if s < t and Z[t][0] > Z[t-1][0]: Z[t] = (Z[t][0]-1, Z[t][1])
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
                
        # for i in range(self.m):
        #     for j in range(self.n):
        #         ic(i, j, C[i][j])
        self.complexes = C

    # def complexes_generator_legacy(self):
    #     """compute complexes"""
    #     # C[i][j], i in range(m), j in range(n)
    #     # i: time index
    #     # j: layer index
    #     C = [[set() for j in range(self.n)] for i in range(self.m)]
    #     # C is a list of lists of sets, 
    #     # each set contains strings of vertices, 
    #     # each string represents a simplex
    #     with open(self.txf, 'r') as f:
    #         filt = [line.rstrip() for line in f]
    #         # line is in form of
    #         # dim birth n m v_0...v_dim
    #         # filt=f.read().rstrip().split('\n') #filtration
    #     if filt[0] == '':
    #         return
    #     for i in range(len(filt)):
    #         # data=filt[i].rstrip().split()
    #         data = filt[i].split()
    #         if data[0] == '#': continue # skip comments
    #         if self.dim + 1 < int(data[0]): continue # skip higher dimensions
    #         # if self.dim < 1 and data[0] == '2': continue 
    #         # if self.dim < 2 and data[0] == '3': continue
    #         # data[3]: horizontal index
    #         # data[2]: vertical index
    #         C[int(data[3])][int(data[2])].add(' '.join(sorted(data[4:])))
    #         # TODO: notice that this is not affected by self.m and self.n. 
    #         # TODO: maybe we should set the ladder length automatically from the filtration file
    #         # TODO: check if sorted here is sufficient, or if it is necessary to sort
    #     # up to now, C contains each simplices newly added at each step.
    #     for i in range(1, self.m): # Reconstruct the lower layer
    #         C[i][0] = C[i][0] | C[i-1][0] # union
    #     for j in range(1, self.n): # reconstruct the leftest column
    #         # for self.n=2, we only need to reconstruct the first column
    #         C[0][j] = C[0][j] | C[0][j-1]
    #     # Reconstruction of the upper layer staring from the second column
    #     for i in range(1, self.m):
    #         for j in range(1, self.n):
    #             C[i][j] = C[i][j] | C[i-1][j] | C[i][j-1]
    #     self.complexes = C

    

    @staticmethod
    def intv_support_num(I):
        b0, d0 = I[0]
        b1, d1 = I[1]
        return max(d1-b1+1,0)+max(d0-b0+1,0)

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
        # print(self.variables['NodeToStr'])
        # return NodeToStr
    
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

    @staticmethod
    def _fzz_executor(input_file_path, clean_up=True):
        """https://github.com/taohou01/fzz/"""
        original_dir = os.getcwd()
        # get the absolute path of the directory of the input file
        input_dir = os.path.abspath(os.path.dirname(input_file_path))
        os.chdir(input_dir)
        subprocess.run([FZZ_BINARY_PATH,input_file_path])
        if clean_up:
            delete_file(input_file_path)
        os.chdir(original_dir)
        return f"{input_file_path[:-4]}_pers" # do not change this line as the file name is controled by fzz. if you would like to change it, change the filename of the output first
    
    def fzz_generator_upper(self):
        # upper layer
        m=self.m
        # n=self.n
        # remove the extension of self.txf and add _FZZ to the filename, use .txt as the extension
        # do not use [:-4], as the length of extension may change
        fzz_input_file_name = filepath_generator(dirname=self.txf_dir,filename=self.txf_basename_wo_ext + '_FZZ_upper',extension='txt')
        self.variables['d_ss'] = {}
        # self.variables['S'] is used to align the index in the commutative ladder
        # with the index when all simplicial complex get expanded and inserted one by one
        # and then computed using fzz
        self.variables['S'] = [0, self.variables['NodeToStr'][(0, 1)][1]] # (0,1), notice the difference
        # ic(self.variables['S'])
        for i in range(m-1): 
            self.variables['S'].append(self.variables['S'][-1]+self.variables['PathToStr'][(i, 1, i+1, 1)][1])
            # ic(i,self.variables['S'])
        self.variables['S'].append(self.variables['S'][-1]+1)
        # ic(self.variables['S'])
        for i in range(m):
            for j in range(i, m): 
                self.variables['d_ss'][(i, j)]=0
        with open(fzz_input_file_name, 'w') as f:
            # add the simplices at (0,1) line by line
            f.write(self.variables['NodeToStr'][(0, 1)][0]) 
             # add all simplices from (0,1) to (m-1,1) line by line and by insertion order
            f.write(self.variables['PathToStr'][(0, 1, m-1, 1)][0])
        return self._fzz_executor(fzz_input_file_name,clean_up=self.clean_up)
    
    def fzz_generator_lower(self):
        # lower layer
        m=self.m
        # n=self.n
        fzz_input_file_name = filepath_generator(dirname=self.txf_dir,filename=self.txf_basename_wo_ext + '_FZZ_lower',extension='txt')
        self.variables['d_ss']={}
        self.variables['S'] = [0, self.variables['NodeToStr'][(0, 0)][1]] # (0,0), notice the difference
        for i in range(m-1): 
            self.variables['S'].append(self.variables['S'][-1]+self.variables['PathToStr'][(i, 0, i+1, 0)][1])
        self.variables['S'].append(self.variables['S'][-1]+1)
        for i in range(m):
            for j in range(i, m): self.variables['d_ss'][(i, j)]=0
        with open(fzz_input_file_name, 'w') as f:
            f.write(self.variables['NodeToStr'][(0, 0)][0])
            f.write(self.variables['PathToStr'][(0, 0, m-1, 0)][0])
        return self._fzz_executor(fzz_input_file_name,clean_up=self.clean_up)

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
        with open(file_path, 'w') as file:
            for key, value in NodeToStr.items():
                file.write(f"{key}: {value[0]}")

    def deco(self):
        #n = self.n
        m = self.m
        dim = self.dim
        self.complexes_generator()
        self.node2str_generator()
        # self.write_node_to_str(self.variables['NodeToStr'], "NodeToStr.txt")
        self.path2str_generator()
        print("全ての道の差分リストを構築")
        # self.write_node_to_str(self.variables['NodeToStr'], "NodeToStr.txt")
        # self.write_node_to_str(self.variables['PathToStr'], "PathToStr.txt")

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
        for interval in barcode:
            current_dim, p, q = map(int, interval.rstrip().split())
            if current_dim != dim:
                continue
            for j in range(m): 
                if self.variables['S'][j]<p and p<=self.variables['S'][j+1]: 
                    b=j; 
                    break
            for j in range(-1,m): # here we shift the death time earlier by one unit
                # set d to be 
                if self.variables['S'][j+1]<=q and q<self.variables['S'][j+2]: 
                    d=j; 
                    break

                # if self.variables['S'][d1+1]<p or q<self.variables['S'][d1+2]: 
                #     continue
            if b<=d:
                self.variables['d_ss'][(b, d)]+=1
        e=(m, -1)
        self.variables['c_ss'][(e, (-1, m))]=0
        for i in range(m):
            self.variables['c_ss'][(e, (i, m))]=0
            self.variables['c_ss'][(e, (-1, i))]=0
        for l in range(m-1, -1, -1):
            for b in range(m-l):
                d=b+l
                self.variables['c_ss'][(e, (b, d))]=self.variables['d_ss'][(b, d)]+self.variables['c_ss'][(e, (b-1, d))]+self.variables['c_ss'][(e, (b, d+1))]-self.variables['c_ss'][(e, (b-1, d+1))]

        fzz_output_lower=self.fzz_generator_lower()
        with open(fzz_output_lower, 'r') as f:
            barcode = [line.rstrip() for line in f]
        if self.clean_up:
            delete_file(fzz_output_lower)
        for interval in barcode:
            current_dim, p, q = map(int, interval.rstrip().split())
            if current_dim != dim:
                continue
        # for i in range(len(barcode)):
        #     data=barcode[i].rstrip().split()
        #     if int(data[0])!=dim: 
        #         continue
        #     p=int(data[1])
        #     q=int(data[2])
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
        self.variables['c_ss'][((-1, m), e)]=0
        for i in range(m): 
            self.variables['c_ss'][((i, m), e)]=0
            self.variables['c_ss'][((-1, i), e)]=0
        for l in range(m-1, -1, -1):
            for b in range(m-l):
                d=b+l
                self.variables['c_ss'][((b, d), e)]=self.variables['d_ss'][(b, d)]+self.variables['c_ss'][((b-1, d), e)]+self.variables['c_ss'][((b, d+1), e)]-self.variables['c_ss'][((b-1, d+1), e)]

        c=0
        # parallelize this part
        for b0 in range(m):
            for d1 in range(b0, m):
                print('\r進捗率: {0:.2f}％ '.format(100*c/((m+1)*m/2)), end='')
                if self.variables['c_ss'][((b0, d1), e)]==0 or self.variables['c_ss'][(e, (b0, d1))]==0: 
                    c+=1
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
                fzz_input_file_name = filepath_generator(dirname=self.txf_dir,filename=self.txf_basename_wo_ext + f'_FZZ_{b0}_{d1}',extension='txt')
                with open(fzz_input_file_name, 'w') as f:
                    f.write(self.variables['NodeToStr'][(0, 1)][0])
                    if 0<d1:
                        f.write(self.variables['PathToStr'][(0, 1, d1, 1)][0])
                    f.write(self.variables['PathToStr'][(d1, 1, b0, 0)][0])
                    if b0<m-1:
                        f.write(self.variables['PathToStr'][(b0, 0, m-1, 0)][0])
                fzz_output_loop=self._fzz_executor(fzz_input_file_name,clean_up=self.clean_up)
                with open(fzz_output_loop, 'r') as f:
                    barcode = [line.rstrip() for line in f]
                if self.clean_up:
                    delete_file(fzz_output_loop)
                for interval in barcode:
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
                c+=1
        print('\r進捗率: {0:.2f}％ '.format(100*c/((m+1)*m/2)))
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
                ans_ss += ((-1)**sl)*self.variables['c_ss'][js]
            delt_ss[I] = ans_ss
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

