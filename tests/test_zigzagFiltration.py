import dionysus as d
import pytest
from classia.filtration import SimplicialComplex, ZigzagFiltration


def test_zigzag_homology_persistence():
    scs = []
    for i in range(5):
        obj = SimplicialComplex()
        scs.append(obj)

    scs[0].from_simplices([(1,)])
    scs[1].from_simplices([(0,), (1,)])
    scs[2].from_simplices([(1,)])
    scs[3].from_simplices([(0,), (1,)])
    scs[4].from_simplices([(0,), (1,), (2,), (0, 1), (0, 2), (1, 2)])

    a = ZigzagFiltration(*scs)

    f = d.Filtration(a.ensemble)
    times = a.all_time_sequences()

    zz, dgms, cells = d.zigzag_homology_persistence(f, times)

    bd=[]
    for i, dgm in enumerate(dgms):
        print("Dimension:", i)
        for p in dgm:
            bd.append(p)
    assert bd[1].birth == 3
    assert bd[1].death == 4

