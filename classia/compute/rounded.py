def multiplicity(self,I,round:int,c_ss):
        b0,d0=I[0]
        b1,d1=I[1]
        C=self.C
        if d1 == -1 and b0 == d0:
            self.pp.c_ss[I] = self.getPD([C[b0][0]])
        elif d0 == -1 and b1 == d1:
            self.pp.c_ss[I] = self.getPD([C[b1][1]])
        elif d1 == -1:
            if round == 0:
                self.pp.c_ss[I] = 0
            elif round == 1:
                if c_ss[((b0, d0-1), (self.m, -1))] >= 1 and c_ss[((b0+1, d0), (self.m, -1))] >= 1:
                    self.pp.c_ss[I] = self.getPD([C[b0][0], C[d0][0]]) 
        elif d0 == -1:
            if round == 0:
                self.pp.c_ss[I] = 0
            elif round == 1:
                if c_ss[((m, -1), (b1, d1-1))] >= 1 and c_ss[((self.m, -1), (b1+1, d1))] >= 1:
                    self.pp.c_ss[I] = self.getPD([C[b1][1], C[d1][1]])
        elif b0 == d0 and b1 == d1:
            if round == 0:
                self.pp.c_ss[I] = 0
            elif round == 1:
                if c_ss[((b0, b0), (self.m, -1))] >= 1 and c_ss[((self.m, -1), (b1, b1))] >= 1:
                    self.pp.c_ss[I] = self.getPD([C[b0][0], C[b1][1]]) 
        elif b0 == b1 and d0 == d1:
            if round == 0:
                self.pp.c_ss[I] = 0
            elif round == 1:
                if c_ss[((b0, d0), (b1, d1-1))] >= 1 and c_ss[((b0+1, d0), (b1, d1))] >= 1:
                    self.pp.c_ss[I] =  self.getPD([C[b0][0], C[d1][1]])    
        elif b1 == d1:
            if round == 1:
                self.pp.c_ss[I] = r = min(c_ss[((b0, d0-1), (b1, b1))],c_ss[((b0, d0), (self.m, -1))])
                if r == 0:
                    pass
                elif r != 0: 
                    self.pp.c_ss[I] = self.getPD([C[b0][0], C[d1][1] | C[d0][0]])
                    if self.pp.c_ss[I] == r:
                        self.pp.p += 1
                    elif self.pp.c_ss[I] != r:
                        self.pp.c_ss[I] = self.toDio([C[b1][1], C[b0][0], C[d0][0]])
                        self.pp.q += 1
            else:
                pass
        elif b0 == d0:
            if round == 1:
                self.pp.c_ss[I] = r = min(c_ss[((self.m, -1), (b1, d1))],c_ss[((d0, d0), (b1+1, d1))])
                if r == 0:
                    pass
                elif r != 0:
                    self.pp.c_ss[I] = self.getPD([C[b1][1] & C[b0][0], C[d1][1]])
                    if self.pp.c_ss[I] == r:
                        self.pp.p += 1
                    elif self.pp.c_ss[I] != r:
                        self.pp.c_ss[I] = self.toDio([C[b1][1], C[d1][1], C[d0][0]])
                        self.pp.q += 1
            else:
                pass
        elif b0 == d1:
            if round == 1:
                self.pp.c_ss[I] = r = min(c_ss[((b0, d0-1), (b1, d1))],c_ss[((b0, d0), (b1+1, d1))])
                if r == 0: 
                    pass
                elif r != 0:
                    self.pp.c_ss[I] = self.getPD([C[b1][1] & C[b0][0], C[d1][1] | C[d0][0]])
                    if self.pp.c_ss[I] == r:
                        self.pp.p += 1
                    elif self.pp.c_ss[I] != r:
                        self.pp.c_ss[I] = self.toDio([C[b1][1], C[d1][1], C[b0][0], C[d0][0]])
                        self.pp.q += 1
            else:
                pass
        elif b0 == b1:
            if round == 1:
                self.pp.c_ss[I] = r = min(c_ss[((b0, d0-1), (b1, d1))],
                                c_ss[((b0, d0), (b1, d1-1))], c_ss[((b0+1, d0), (b1, d1))])
                if r == 0: 
                    pass
                elif r != 0:
                    self.pp.c_ss[I] = self.getPD([C[b0][0], C[d1][1] | C[d0][0]])
                    if self.pp.c_ss[I] == r:
                        self.pp.p += 1
                    elif self.pp.c_ss[I] != r:
                        c_ss[I] = self.toDio([C[d1][1], C[b0][0], C[d0][0]])
                        self.pp.q += 1
            else:
                pass
        elif d0 == d1:
            if round == 1:
                self.pp.c_ss[I] = r = min(c_ss[((b0, d0), (b1+1, d1))],
                                c_ss[((b0+1, d0), (b1, d1))], c_ss[((b0, d0), (b1, d1-1))])
                if r == 0: 
                    pass
                elif r != 0:
                    self.pp.c_ss[I] = self.getPD([C[b1][1] & C[b0][0], C[d1][1]])
                    if self.pp.c_ss[I] == r:
                        self.pp.p += 1
                    elif self.pp.c_ss[I] != r:
                        self.pp.c_ss[I] = self.toDio([C[b1][1], C[d1][1], C[b0][0]])
                        self.pp.q += 1
            else:
                pass
        else:
            if round == 2:
                self.pp.c_ss[I] = r = min(c_ss[((b0, d0), (b1+1, d1))], c_ss[((b0+1, d0), (b1, d1))],
                                c_ss[((b0, d0), (b1, d1-1))], c_ss[((b0, d0-1), (b1, d1))])
            if r == 0: continue
            c_ss[I] = getPD([C[b1][1] & C[b0][0], C[d1][1] | C[d0][0]])
            if c_ss[I] == r:
                p += 1; continue
            c_ss[I] = toDio(
                [C[b1][1], C[d1][1], C[b0][0], C[d0][0]]); q += 1