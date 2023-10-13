
    def path2str_generator(self):
        # PathToStr=CompressedDict()
        PathToStr={}
        # Compressed Dictionary to store string representations of paths 
        # Starting from CompressedDict instead of copying from dict to reduce memory usage
        m=self.m
        n=self.n
        s=''        
        if not hasattr(self, 'complexes'):
            raise AttributeError("self.complexes is not defined. Please run self.complexes_generator() first.")       
        C=self.complexes # C is a list of lists of sets, each set contains strings of vertices, each string represents a simplex
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
        #get memory usage
        # from ..utils import print_memory_usage
        # print_memory_usage(PathToStr)
        logging.debug("PathToStr dict object generated.")
        # breakpoint()
        if isinstance(PathToStr, dict):
            PathToStr = CompressedDict(PathToStr)
        if self.enable_multi_processing:
            from commutazzio.utils import CompressedDictManager
            manager = CompressedDictManager()
            manager.start()
            return manager.CompressedDict(PathToStr)
        else:
            return PathToStr