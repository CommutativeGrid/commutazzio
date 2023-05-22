def computePD(i):
    import dionysus as d
    import numpy as np
    np.random.seed(42)
    f = d.Filtration([[0], [1], [0,1], [2], [0,2], [1,2]])
    times = [[.4, .6, .7], [.1], [.9], [.9], [.9], [.9]]
    zz, dgms, cells = d.zigzag_homology_persistence(f, times)
    return np.random.randint(1,20)

