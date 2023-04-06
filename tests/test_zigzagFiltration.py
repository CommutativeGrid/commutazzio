import dionysus as d
import pytest
from camelia.filtration import SimplicialComplex, ZigzagFiltration


def test_zigzag_homology_persistence():
    scs = []
    for i in range(5):
        obj = SimplicialComplex()
        scs.append(obj)

    # Build SimplicialComplex objects
    scs[0].from_simplices([(1,)])
    scs[1].from_simplices([(0,), (1,)])
    scs[2].from_simplices([(1,)])
    scs[3].from_simplices([(0,), (1,)])
    scs[4].from_simplices([(0,), (1,), (2,), (0, 1), (0, 2), (1, 2)])

    # Create a ZigzagFiltration object from the SimplicialComplex objects
    a = ZigzagFiltration(*scs)

    # Convert ZigzagFiltration object to Filtration object for use with dionysus library
    f = d.Filtration(a.ensemble)

    # Get time sequence of all ZigzagFiltration objects
    times = a.all_time_sequences()

    # Compute zigzag persistence
    zz, dgms, cells = d.zigzag_homology_persistence(f, times)

    # Process the computed persistence diagrams
    bd=[]
    for i, dgm in enumerate(dgms):
        print("Dimension:", i)
        for p in dgm:
            bd.append(p)

    # Assert that the second bar in the second dimension has birth time 3 and death time 4
    assert bd[1].birth == 3
    assert bd[1].death == 4
