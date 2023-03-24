# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 17:29:27 2022

@author: kasumi
"""
import dionysus as dio
import pandas as pd
from ..utils import radii_generator,delete_file
import numpy as np
from pathos.multiprocessing import ProcessingPool as Pool
from multiprocessing import Manager
import subprocess, os, json, sys
#import gc garbage collection

def toList(st):
    return list(map(int, st.split(',')))

class CommutativeLadderKinjiSS():
    def __init__(self, txf, **kwargs):
        # , txf=None, m=None, n=2, dim=1):
        self.txf = txf # filtration file
        self.m = kwargs.get('ladder_length', 10) # default length is 10
        self.ladder_length = self.m
        self.n = 2 # two layers by default
        self.radii = self.radii_compute(**kwargs)
        self.dim = kwargs.get('dim', 1)
        self.intv = self.interval_generator()
        self.mproc = kwargs.get('mproc')
        self.variables={'cov':{},'c_ss':{}}
        self.cover_generator()
        self.delt_ss = self.deco()
        self.compute_dec_obj()
        self.compute_connecting_lines()
        self.compute_dotdec()
        self.compute_plot_dots()
        self.parameters = self.parameter_setup(**kwargs)

    def parameter_setup(self,**kwargs):
        parameters={k:v for k,v in kwargs.items()}
        parameters.update({'radii': self.radii})
        parameters.update({'dots': self.dots})
        parameters.update({'lines': self.lines})
        return parameters

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

    @staticmethod
    def radii_compute(**kwargs):
        radii = kwargs.get("radii")
        if radii is not None:
            return np.array(radii)
        start = kwargs.get("start")
        end = kwargs.get("end")
        ladder_length = kwargs.get("ladder_length")
        radii = radii_generator(start,end,ladder_length)
        return radii

    def plot_js(self):
        """Pipeline for plot using native JavaScript"""
        # self.delt_ss=self.deco()
        self.save2js()

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

    # @staticmethod
    # def sizeSupp(X):
    #     s = 0
    #     for i in range(len(X)):
    #         if X[i][1] == -1: continue
    #         s += X[i][1]-X[i][0]+1
    #     return s

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

    @staticmethod
    def _toDio(dim, cpxList):
        U = set()
        for K in cpxList: U = U | K
        U = list(U); times = []
        for i in range(len(U)):
            times.append([]); ex = 0
            for j in range(len(cpxList)):
                if (ex == 0 and (U[i] in cpxList[j])) or (ex == 1 and (U[i] not in cpxList[j])):
                    times[i].append(j/10)
                    ex = (ex+1) % 2
        f = dio.Filtration(list(map(toList, U)))
        _, dgms, _ = dio.zigzag_homology_persistence(f, times)
        c = 0
        for i, dgm in enumerate(dgms):
            if i == dim:
                for p in dgm:
                    if p.birth == 0 and p.death == float('inf'): c += 1
        return c

    @staticmethod
    def _getPD(dim, cpxList):
        simplices = []
        U = list(cpxList[0])
        for C in U: simplices.append((toList(C), 0))
        if len(cpxList) == 2:
            U = list(cpxList[1]-cpxList[0])
            for C in U: simplices.append((toList(C), 1))
        f = dio.Filtration()
        for vertices, time in simplices: f.append(dio.Simplex(vertices, time))
        f.sort()
        m = dio.homology_persistence(f)
        dgms = dio.init_diagrams(m, f)
        c = 0
        for i, dgm in enumerate(dgms):
            if i == dim:
                for p in dgm:
                    if p.birth == 0 and p.death == float('inf'): c += 1
        return c

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
        """compute complexes"""
        # C[j][i], j in range(m), i in range(n)
        C = [[set() for j in range(self.n)] for i in range(self.m)]
        with open(self.txf, 'r') as f:
            filt = [line.rstrip() for line in f]
            # line is in form of
            # dim birth n m v_0...v_dim
            # filt=f.read().rstrip().split('\n') #filtration
        if filt[0] == '':
            return
        for i in range(len(filt)):
            # data=filt[i].rstrip().split()
            data = filt[i].split()
            if data[0] == '#': continue
            if self.dim < 1 and data[0] == '2': continue
            if self.dim < 2 and data[0] == '3': continue
            C[int(data[3])][int(data[2])].add(' '.join(sorted(data[4:])))
        for i in range(1, self.m):
            C[i][0] = C[i][0] | C[i-1][0]
        for j in range(1, self.n):
            C[0][j] = C[0][j] | C[0][j-1]
        for i in range(1, self.m):
            for j in range(1, self.n):
                C[i][j] = C[i][j] | C[i-1][j] | C[i][j-1]
        self.complexes = C
        # return C

    

    @staticmethod
    def intv_support_num(I):
        b0, d0 = I[0]
        b1, d1 = I[1]
        return max(d1-b1+1,0)+max(d0-b0+1,0)

    
    # @staticmethod
    # def f(args):
    #     #i,I,C,getPD,toDio,m,dim,c_ss,p,q=args
    #     i=args[0]
    #     print(i.value)
    #     print('\n')
    #     i.value+=1

    @staticmethod
    def multiplicity(args):
        I,Cpart,getPD,toDio,m,c_ss,p,q=args
        C=Cpart
        #print('inside multiplicity', I)
        print(I)
        #print(c_ss)
        b0,d0=I[0]
        b1,d1=I[1]
        if d1 == -1 and b0 == d0:
            c_ss[I] = getPD([C[(b0,0)]])
        elif d0 == -1 and b1 == d1:
            c_ss[I] = getPD([C[(b1,1)]])
        elif d1 == -1:
            if c_ss[((b0, d0-1), (m, -1))] >= 1 and c_ss[((b0+1, d0), (m, -1))] >= 1:
                c_ss[I] = getPD([C[(b0,0)], C[(d0,0)]])
            else:
                c_ss[I] = 0
        elif d0 == -1:
            if c_ss[((m, -1), (b1, d1-1))] >= 1 and c_ss[((m, -1), (b1+1, d1))] >= 1:
                c_ss[I] = getPD([C[(b1,1)], C[(d1,1)]])
            else:
                c_ss[I] = 0
        elif b0 == d0 and b1 == d1:
            if c_ss[((b0, b0), (m, -1))] >= 1 and c_ss[((m, -1), (b1, b1))] >= 1:
                c_ss[I] = getPD([C[(b0,0)], C[(b1,1)]]) 
            else:
                c_ss[I] = 0
        elif b0 == b1 and d0 == d1:
            if c_ss[((b0, d0), (b1, d1-1))] >= 1 and c_ss[((b0+1, d0), (b1, d1))] >= 1:
                c_ss[I] =  getPD([C[(b0,0)], C[(d1,1)]])    
            else:
                c_ss[I] = 0
        elif b1 == d1:
            c_ss[I] = r = min(c_ss[((b0, d0-1), (b1, b1))],c_ss[((b0, d0), (m, -1))])
            if r == 0:
                pass
            elif r != 0: 
                c_ss[I] = getPD([C[(b0,0)], C[(d1,1)] | C[(d0,0)]])
                if c_ss[I] == r:
                    p.value += 1
                elif c_ss[I] != r:
                    c_ss[I] = toDio([C[(b1,1)], C[(b0,0)], C[(d0,0)]])
                    q.value += 1
        elif b0 == d0:
            c_ss[I] = r = min(c_ss[((m, -1), (b1, d1))],c_ss[((d0, d0), (b1+1, d1))])
            if r == 0:
                pass
            elif r != 0:
                c_ss[I] = getPD([C[(b1,1)] & C[(b0,0)], C[(d1,1)]])
                if c_ss[I] == r:
                    p.value += 1
                elif c_ss[I] != r:
                    c_ss[I] = toDio([C[(b1,1)], C[(d1,1)], C[(d0,0)]])
                    q.value += 1
        elif b0 == d1:
            c_ss[I] = r = min(c_ss[((b0, d0-1), (b1, d1))],c_ss[((b0, d0), (b1+1, d1))])
            if r == 0: 
                pass
            elif r != 0:
                c_ss[I] = getPD([C[(b1,1)] & C[(b0,0)], C[(d1,1)] | C[(d0,0)]])
                if c_ss[I] == r:
                    p.value += 1
                elif c_ss[I] != r:
                    c_ss[I] = toDio([C[(b1,1)], C[(d1,1)], C[(b0,0)], C[(d0,0)]])
                    q.value += 1
        elif b0 == b1:
            c_ss[I] = r = min(c_ss[((b0, d0-1), (b1, d1))],
                            c_ss[((b0, d0), (b1, d1-1))], c_ss[((b0+1, d0), (b1, d1))])
            if r == 0: 
                pass
            elif r != 0:
                c_ss[I] = getPD([C[(b0,0)], C[(d1,1)] | C[(d0,0)]])
                if c_ss[I] == r:
                    p.value += 1
                elif c_ss[I] != r:
                    c_ss[I] = toDio([C[(d1,1)], C[(b0,0)], C[(d0,0)]])
                    q.value += 1
        elif d0 == d1:
            c_ss[I] = r = min(c_ss[((b0, d0), (b1+1, d1))],
                            c_ss[((b0+1, d0), (b1, d1))], c_ss[((b0, d0), (b1, d1-1))])
            if r == 0: 
                pass
            elif r != 0:
                c_ss[I] = getPD([C[(b1,1)] & C[(b0,0)], C[(d1,1)]])
                if c_ss[I] == r:
                    p.value += 1
                elif c_ss[I] != r:
                    c_ss[I] = toDio([C[(b1,1)], C[(d1,1)], C[(b0,0)]])
                    q.value += 1
        else:
            c_ss[I] = r = min(c_ss[((b0, d0), (b1+1, d1))], c_ss[((b0+1, d0), (b1, d1))],
                                c_ss[((b0, d0), (b1, d1-1))], c_ss[((b0, d0-1), (b1, d1))])
            if r == 0: 
                pass
            elif r != 0:
                c_ss[I] = getPD([C[(b1,1)] & C[(b0,0)], C[(d1,1)] | C[(d0,0)]])
            if c_ss[I] == r:
                p.value += 1
            elif c_ss[I] != r:
                c_ss[I] = toDio([C[(b1,1)], C[(d1,1)], C[(b0,0)], C[(d0,0)]])
                q.value += 1

    
    # def intv_C_pairing(self,I):
    #     C=self.C
    #     b0,d0=I[0]
    #     b1,d1=I[1]
    #     if d1 == -1 and b0 == d0:
    #         return {(b0,0):C[b0][0]}
    #         #return [C[b0][0]]
    #     elif d0 == -1 and b1 == d1:
    #         return {(b1,1):C[b1][1]}
    #         #return [C[b1][1]]
    #     elif d1 == -1:
    #         return {(b0,0):C[b0][0],(d0,0):C[d0][0]}
    #         #return [C[b0][0], C[d0][0]]
    #     elif d0 == -1:
    #         return {(b1,1):C[b1][1],(d1,1):C[d1][1]}
    #         #return [C[b1][1], C[d1][1]]
    #     elif b0 == d0 and b1 == d1:
    #         return {(b0,0):C[b0][0],(b1,1):C[b1][1]}
    #         #return [C[b0][0], C[b1][1]]
    #     elif b0 == b1 and d0 == d1:
    #         return {(b0,0):C[b0][0],(d1,1):C[d1][1]}
    #         #return [C[b0][0], C[d1][1]]
    #     elif b1 == d1:
    #         return {(b0,0):C[b0][0],(d1,1):C[d1][1],(d0,0):C[d0][0],
    #                 (b1,1):C[b1][1],(b0,0):C[b0][0],(d0,0):C[d0][0]}
    #     elif b0 == d0:
    #         return {(b1,1):C[b1][1],(b0,0):C[b0][0],(d1,1):C[d1][1],
    #                 (b1,1):C[b1][1],(d1,1):C[d1][1],(d0,0):C[d0][0],}
    #     elif b0 == d1:
    #         return {(b1,1):C[b1][1],(b0,0):C[b0][0],(d1,1):C[d1][1],(d0,0):C[d0][0],
    #                 (b1,1):C[b1][1],(d1,1):C[d1][1],(b0,0):C[b0][0],(d0,0):C[d0][0]}
    #     elif b0 == b1:
    #         return {(b0,0):C[b0][0],(d1,1):C[d1][1],(d0,0):C[d0][0],
    #                 (d1,1):C[d1][1],(b0,0):C[b0][0],(d0,0):C[d0][0]}
    #     elif d0 == d1:
    #         return {(b1,1):C[b1][1],(b0,0):C[b0][0],(d1,1):C[d1][1],
    #                 (b1,1):C[b1][1],(d1,1):C[d1][1],(b0,0):C[b0][0]}
    #     else:
    #         return {(b1,1):C[b1][1],(b0,0):C[b0][0],(d1,1):C[d1][1],(d0,0):C[d0][0],
    #                 (b1,1):C[b1][1],(d1,1):C[d1][1],(b0,0):C[b0][0],(d0,0):C[d0][0]}

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
                L.sort(key=lambda x: (len(x.split(' ')),tuple(map(int,x.split(' ')))))  #Q: does the order of same length objects matter?
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

    
    def _fzz_executor(self, input_file_name, delete_input_file=False):
        """https://github.com/taohou01/fzz/"""
        if sys.platform == 'darwin':
            subprocess.run('/Users/hina/Library/CloudStorage/OneDrive-Personal/Documents/KU/commutative-grid/working_dir_cl50/fzz_sandbox/fzz_mac '+ input_file_name, shell=True)
        elif sys.platform == 'linux':
            subprocess.run('./fzz_wsl '+ input_file_name, shell=True)
        if delete_input_file:
            delete_file(input_file_name)
        return f"{input_file_name[:-4]}_pers"

    def fzz_generator_1(self):
        
        m=self.m
        n=self.n
        fzz_input_file_name = f"{self.txf[:-4]}_FZZ.txt"
        self.variables['d_ss'] = {}
        self.variables['S'] = [0, self.variables['NodeToStr'][(0, 1)][1]]
        for i in range(m-1): 
            self.variables['S'].append(self.variables['S'][-1]+self.variables['PathToStr'][(i, 1, i+1, 1)][1])
        self.variables['S'].append(self.variables['S'][-1]+1)
        for i in range(m):
            for j in range(i, m): 
                self.variables['d_ss'][(i, j)]=0
        with open(fzz_input_file_name, 'w') as f:
            f.write(self.variables['NodeToStr'][(0, 1)][0])
            f.write(self.variables['PathToStr'][(0, 1, m-1, 1)][0])
        return self._fzz_executor(fzz_input_file_name)
    
    def fzz_generator_2(self):
        m=self.m
        n=self.n
        fzz_input_file_name = f"{self.txf[:-4]}_FZZ.txt"
        with open(fzz_input_file_name, 'w') as f:
            f.write(self.variables['NodeToStr'][(0, 0)][0])
            f.write(self.variables['PathToStr'][(0, 0, m-1, 0)][0])
        return self._fzz_executor(fzz_input_file_name)

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
        #getPD = self.getPD
        #toDio = self.toDio
        # num_intv = len(self.intv)
        self.complexes_generator()
        # C=self.complexes
        # breakpoint()
        # self.write_list_of_lists_of_sets_to_file("complexes.txt", C)
        # print(C)
        self.node2str_generator()
        # self.write_node_to_str(self.variables['NodeToStr'], "NodeToStr.txt")
        self.path2str_generator()
        print("全ての道の差分リストを構築")
        # self.write_node_to_str(self.variables['NodeToStr'], "NodeToStr.txt")
        # self.write_node_to_str(self.variables['PathToStr'], "PathToStr.txt")
        fzz_output_1=self.fzz_generator_1()
        with open(fzz_output_1, 'r') as f:
            filt = [line.rstrip() for line in f]
        
        for i in range(len(filt)):
            data=filt[i].rstrip().split()
            if int(data[0])!=dim: 
                continue
            p=int(data[1])
            q=int(data[2])
            for j in range(m): 
                if self.variables['S'][j]<p and p<=self.variables['S'][j+1]: 
                    b=j; 
                    break
            for j in range(m): 
                if self.variables['S'][j+1]<=q and q<self.variables['S'][j+2]: 
                    d=j; 
                    break
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

        self.variables['d_ss']={}
        self.variables['S']=[0, self.variables['NodeToStr'][(0, 0)][1]]
        for i in range(m-1): 
            self.variables['S'].append(self.variables['S'][-1]+self.variables['PathToStr'][(i, 0, i+1, 0)][1])
        self.variables['S'].append(self.variables['S'][-1]+1)
        for i in range(m):
            for j in range(i, m): self.variables['d_ss'][(i, j)]=0


        fzz_output_2=self.fzz_generator_2()
        with open(fzz_output_2, 'r') as f:
            filt = [line.rstrip() for line in f]
        for i in range(len(filt)):
            data=filt[i].rstrip().split()
            if int(data[0])!=dim: 
                continue
            p=int(data[1])
            q=int(data[2])
            for j in range(m): 
                if self.variables['S'][j]<p and p<=self.variables['S'][j+1]: 
                    b=j; 
                    break
            for j in range(m): 
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
    
                fzz_input_file_name = f"{self.txf[:-4]}_FZZ.txt"
                with open(fzz_input_file_name, 'w') as f:
                    f.write(self.variables['NodeToStr'][(0, 1)][0])
                    if 0<d1:
                        f.write(self.variables['PathToStr'][(0, 1, d1, 1)][0])
                    f.write(self.variables['PathToStr'][(d1, 1, b0, 0)][0])
                    if b0<m-1:
                        f.write(self.variables['PathToStr'][(b0, 0, m-1, 0)][0])
                fzz_output_3=self.fzz_generator_3()
                with open(fzz_output_3, 'r') as f:
                    filt = [line.rstrip() for line in f]
                for i in range(len(filt)):
                    data=filt[i].rstrip().split()
                    if int(data[0])!=dim: 
                        continue
                    p=int(data[1])
                    q=int(data[2])
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
                    container.loc[len(container)] = [j+1, i+1, D, 'D',] #self.radii[i], self.radii[j]]
                if U != 0:
                    container.loc[len(container)] = [i+1, j+1, U, 'U',] #self.radii[i], self.radii[j]]
        self.dots= container

    def save2js(self, mode='support_only'):
        """Save the data to js file.

        Parameters
        ----------
        mode : str
            'support_only' : only save non-zero entries
            'all' : save all entries
        """
        m= self.m
        with open(self.txf[:-4]+'.js', 'w+') as f:
            # first line in the js file
            f.write('let siz='+str(m)+', dec={};\n')
            if mode == 'support_only':
                for I in self.intv:
                    if self.delt_ss[I] != 0:  # write to file only if multiplicity is not zero
                        S= f"{I[0][0]},{I[0][1]},{I[1][0]},{I[1][1]}"
                        # S=str(I[0][0])+','+str(I[0][1])+','+str(I[1][0])+','+str(I[1][1])
                        f.write(f'dec["{S}"]={str(self.delt_ss[I])};\n')
            elif mode == 'all':
                for I in self.intv:
                    S= f"{I[0][0]},{I[0][1]},{I[1][0]},{I[1][1]}"
                    # S=str(I[0][0])+','+str(I[0][1])+','+str(I[1][0])+','+str(I[1][1])
                    f.write(f'dec["{S}"]={str(self.delt_ss[I])};\n')
                    # f.write('dec["'+S+'"]='+str(self.delt_ss[I])+';\n')
        print(f"Results written to {self.txf[:-4]+'.js'}")



if __name__ == '__main__':
    a = CommutativeLadderKinjiSS('./data/fcc_7_0.5_1_10.fil', m=10)
    # a.temp()
    # a.pipeline()
