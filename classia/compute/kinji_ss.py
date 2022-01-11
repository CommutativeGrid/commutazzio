# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 17:29:27 2022

@author: kasumi
"""
import dionysus as dio
import pandas as pd


class commutative_ladder_kinji_ss():
    def __init__(self, txf=None, m=None, n=2, dim=1):
        self.txf = txf
        self.m = m
        self.n = n
        self.dim = dim
        self.intv = self.interval_generator()
        self.cov = self.cover_generator()
        self.delt_ss = self.deco()
        self.compute_dec_obj()
        self.compute_connecting_lines()
        self.compute_dotdec()
        self.compute_plot_dots()

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

    def plot_js(self):
        """Pipeline for plot using native JavaScript"""
        # self.delt_ss=self.deco()
        self.save2js()

    def interval_generator(self):
        """Generate intervals"""
        n = self.n  # vertical use !n in debug mode
        m = self.m  # horizontal
        intv = []
        for k in range(n):
            for birth in range(m):
                for death in range(birth, m):
                    I = [(m, -1) for j in range(k)]
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
        intv.sort(key=self.sizeSupp)
        print("全"+str(len(intv))+"個の区間表現を構築")
        return intv

    @staticmethod
    def sizeSupp(X):
        s = 0
        for i in range(len(X)):
            if X[i][1] == -1: continue
            s += X[i][1]-X[i][0]+1
        return s

    def cover_generator(self):
        """generate interval covers"""
        cov = {}
        n = self.n
        m = self.m
        for I in self.intv:
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
        return cov

    @staticmethod
    def toList(st):
        return list(map(int, st.split(',')))

    # @staticmethod
    def toDio(self, cpxList):
        U = set()
        for K in cpxList: U = U | K
        U = list(U); times = []
        for i in range(len(U)):
            times.append([]); ex = 0
            for j in range(len(cpxList)):
                if (ex == 0 and (U[i] in cpxList[j])) or (ex == 1 and (U[i] not in cpxList[j])):
                    times[i].append(j/10)
                    ex = (ex+1) % 2
        f = dio.Filtration(list(map(self.toList, U)))
        _, dgms, _ = dio.zigzag_homology_persistence(f, times)
        c = 0
        for i, dgm in enumerate(dgms):
            if i == self.dim:
                for p in dgm:
                    if p.birth == 0 and p.death == float('inf'): c += 1
        return c

    # @staticmethod
    def getPD(self, cpxList):
        simplices = []
        U = list(cpxList[0])
        for C in U: simplices.append((self.toList(C), 0))
        if len(cpxList) == 2:
            U = list(cpxList[1]-cpxList[0])
            for C in U: simplices.append((self.toList(C), 1))
        f = dio.Filtration()
        for vertices, time in simplices: f.append(dio.Simplex(vertices, time))
        f.sort()
        m = dio.homology_persistence(f)
        dgms = dio.init_diagrams(m, f)
        c = 0
        for i, dgm in enumerate(dgms):
            if i == self.dim:
                for p in dgm:
                    if p.birth == 0 and p.death == float('inf'): c += 1
        return c
    # @staticmethod

    def join_intv(self, X, Y):
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

    def deco(self):
        n = self.n
        m = self.m
        dim = self.dim
        getPD = self.getPD
        toDio = self.toDio
        num_intv = len(self.intv)
        C = [[set() for j in range(n)] for i in range(m)]
        with open(self.txf, 'r') as f:
            filt = [line.rstrip() for line in f]
            # filt=f.read().rstrip().split('\n') #filtration
        if filt[0] == '':
            return
        for i in range(len(filt)):
            # data=filt[i].rstrip().split()
            data = filt[i].split()
            if data[0] == '#': continue
            if dim < 1 and data[0] == '2': continue
            if dim < 2 and data[0] == '3': continue
            C[int(data[3])][int(data[2])].add(','.join(sorted(data[4:])))
        for i in range(1, m):
            C[i][0] = C[i][0] | C[i-1][0]
        for j in range(1, n):
            C[0][j] = C[0][j] | C[0][j-1]
        for i in range(1, m):
            for j in range(1, n):
                C[i][j] = C[i][j] | C[i-1][j] | C[i][j-1]
        c = 0; p = 0; q = 0; r = 0; c_ss = {}; delt_ss = {};
        for I in self.intv:
            print(
                '\r進捗: {0}/{1} | 処理中: {2} | zig回避: {3} | zigした: {4} '.format(c, num_intv, I, p, q), end='')
            b0, d0 = I[0]; b1, d1 = I[1]; c += 1;
            if d1 == -1 and b0 == d0:
                c_ss[I] = getPD([C[b0][0]])
            elif d0 == -1 and b1 == d1:
                c_ss[I] = getPD([C[b1][1]])
            elif d1 == -1:
                c_ss[I] = getPD([C[b0][0], C[d0][0]]) if c_ss[(
                    (b0, d0-1), (m, -1))] >= 1 and c_ss[((b0+1, d0), (m, -1))] >= 1 else 0
            elif d0 == -1:
                c_ss[I] = getPD([C[b1][1], C[d1][1]]) if c_ss[(
                    (m, -1), (b1, d1-1))] >= 1 and c_ss[((m, -1), (b1+1, d1))] >= 1 else 0
            elif b0 == d0 and b1 == d1:
                c_ss[I] = getPD([C[b0][0], C[b1][1]]) if c_ss[(
                    (b0, b0), (m, -1))] >= 1 and c_ss[((m, -1), (b1, b1))] >= 1 else 0
            elif b0 == b1 and d0 == d1:
                c_ss[I] = getPD([C[b0][0], C[d1][1]]) if c_ss[(
                    (b0, d0), (b1, d1-1))] >= 1 and c_ss[((b0+1, d0), (b1, d1))] >= 1 else 0
            elif b1 == d1:
                c_ss[I] = r = min(c_ss[((b0, d0-1), (b1, b1))],
                                  c_ss[((b0, d0), (m, -1))])
                if r == 0: continue
                c_ss[I] = getPD([C[b0][0], C[d1][1] | C[d0][0]])
                if c_ss[I] == r:
                    p += 1; continue
                c_ss[I] = toDio([C[b1][1], C[b0][0], C[d0][0]]); q += 1
            elif b0 == d0:
                c_ss[I] = r = min(c_ss[((m, -1), (b1, d1))],
                                  c_ss[((d0, d0), (b1+1, d1))])
                if r == 0: continue
                c_ss[I] = getPD([C[b1][1] & C[b0][0], C[d1][1]])
                if c_ss[I] == r:
                    p += 1; continue
                c_ss[I] = toDio([C[b1][1], C[d1][1], C[d0][0]]); q += 1
            elif b0 == d1:
                c_ss[I] = r = min(c_ss[((b0, d0-1), (b1, d1))],
                                  c_ss[((b0, d0), (b1+1, d1))])
                if r == 0: continue
                c_ss[I] = getPD([C[b1][1] & C[b0][0], C[d1][1] | C[d0][0]])
                if c_ss[I] == r:
                    p += 1; continue
                c_ss[I] = toDio(
                    [C[b1][1], C[d1][1], C[b0][0], C[d0][0]]); q += 1
            elif b0 == b1:
                c_ss[I] = r = min(c_ss[((b0, d0-1), (b1, d1))],
                                  c_ss[((b0, d0), (b1, d1-1))], c_ss[((b0+1, d0), (b1, d1))])
                if r == 0: continue
                c_ss[I] = getPD([C[b0][0], C[d1][1] | C[d0][0]])
                if c_ss[I] == r:
                    p += 1; continue
                c_ss[I] = toDio([C[d1][1], C[b0][0], C[d0][0]]); q += 1
            elif d0 == d1:
                c_ss[I] = r = min(c_ss[((b0, d0), (b1+1, d1))],
                                  c_ss[((b0+1, d0), (b1, d1))], c_ss[((b0, d0), (b1, d1-1))])
                if r == 0: continue
                c_ss[I] = getPD([C[b1][1] & C[b0][0], C[d1][1]])
                if c_ss[I] == r:
                    p += 1; continue
                c_ss[I] = toDio([C[b1][1], C[d1][1], C[b0][0]]); q += 1
            else:
                c_ss[I] = r = min(c_ss[((b0, d0), (b1+1, d1))], c_ss[((b0+1, d0), (b1, d1))],
                                  c_ss[((b0, d0), (b1, d1-1))], c_ss[((b0, d0-1), (b1, d1))])
                if r == 0: continue
                c_ss[I] = getPD([C[b1][1] & C[b0][0], C[d1][1] | C[d0][0]])
                if c_ss[I] == r:
                    p += 1; continue
                c_ss[I] = toDio(
                    [C[b1][1], C[d1][1], C[b0][0], C[d0][0]]); q += 1
        print(
            '\r進捗: {0}/{1} | 処理中: - | zig回避: {2} | zigした: {3} '.format(c, num_intv, p, q))
        for I in self.intv:
            t = len(self.cov[I]); subs = 1 << t; ans_ss = 0
            for s in range(subs):
                js = I; sl = 0
                for j in range(t):
                    if (1 << j) & s:
                        sl += 1
                        js = self.join_intv(js, self.cov[I][j])
                ans_ss += ((-1)**sl)*c_ss[js]
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
                    container.loc[len(container)] = [j+1, i+1, D, 'D']
                if U != 0:
                    container.loc[len(container)] = [i+1, j+1, U, 'U']
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
    a = commutative_ladder_kinji_ss('./data/fcc_7_0.5_1_10.fil', m=10)
    # a.temp()
    # a.pipeline()
