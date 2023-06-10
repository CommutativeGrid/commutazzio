import pickle

class CommutativeGridPreCompute():
    # G_{m,n}
    def __init__(self,m:int,n:int=2):
        # m: horizontal length
        # n: height
        # n=2 for commutative ladder 
        self.m=m
        self.n=n
        #raise error if not 1<=m<=999 and 1<=n<=999
        if not (1<=m<=999 and 1<=n<=999):
            raise ValueError("m and n should be within [1,999]")
        self.intv = self.interval_generator()
        self.variables={'cov':{},'c_ss':{}}
        self.cover_generator()
        self.c_ss_initializer()

    def get_intervals(self):
        return self.intv

    def get_variables(self):
        return self.variables

    def save_intv_to_file(self,dirpath):
        """save intv to file"""
        filename = f"intv_{self.m:03d}_{self.n:03d}.pkl"
        filepath = f"{dirpath}/{filename}"
        with open(filepath, "wb") as f:
            pickle.dump(self.intv,f)
    
    def save_variables_to_file(self, dirpath):
        """save variables to file"""
        # prefill number with zeros, three digits in total.
        filename = f"variables_{self.m:03d}_{self.n:03d}.pkl"
        filepath = f"{dirpath}/{filename}"
        with open(filepath, "wb") as f:
            pickle.dump(self.variables, f)
    
    def interval_generator(self):
        """Generate intervals"""
        n = self.n  # vertical height, use !n in debug mode
        m = self.m  # horizontal length, 2 by default
        intv = []
        # will be a list of tuples.
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
        """generate interval covers
        some values of c_ss is initialized
        """
        cov = {} # will be a dict
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

        self.variables['cov']=cov
    
    def c_ss_initializer(self):
        m=self.m
        c_ss={}
        for I in self.intv:
            c_ss[I]=0
        e=(m, -1)
        c_ss[(e, (-1, m))]=0
        for i in range(m):
            c_ss[(e, (i, m))]=0
            c_ss[(e, (-1, i))]=0

        c_ss[((-1, m), e)]=0
        for i in range(m): 
            c_ss[((i, m), e)]=0
            c_ss[((-1, i), e)]=0
        self.variables['c_ss']=c_ss