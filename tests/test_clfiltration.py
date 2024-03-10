from commutazzio.filtration import points_to_clfiltration_chro, CLFiltration, SimplicialComplex
from gudhi import SimplexTree as gudhi_SimplexTree
from commutazzio.compute import CLInvariants
import numpy as np
import pytest



@pytest.fixture
def clf_example():
    cc=CLFiltration()
    f2=gudhi_SimplexTree()
    f1=gudhi_SimplexTree()
    f2.insert([1,2],1)
    f2.insert([2,3],2)
    f2.insert([3,1],2)
    f2.insert([1,2,3],3)
    f1.insert([1],1)
    f1.insert([1,3],2)
    f1.insert([1,2],3)
    f1.insert([2,3],3)
    cc.ladder_length = 3
    cc.upper = f2
    cc.lower = f1
    cc.metadata = {'test':[[1,2,3]]}
    return cc


def test_upper_row(clf_example):
    upper = clf_example.upper
    # test that [1, 2] simplex has filtration value 1
    assert upper.filtration([1, 2]) == 1
    # test that [2, 3] simplex has filtration value 2
    assert upper.filtration([2, 3]) == 2
    # test that [3, 1] simplex has filtration value 2
    assert upper.filtration([3, 1]) == 2
    # test that [1, 2, 3] simplex has filtration value 3
    assert upper.filtration([1, 2, 3]) == 3

def test_lower_row(clf_example):
    lower = clf_example.lower
    # test that [1] simplex has filtration value 1
    assert lower.filtration([1]) == 1
    # test that [1, 3] simplex has filtration value 2
    assert lower.filtration([1, 3]) == 2
    # test that [1, 2] simplex has filtration value 3
    assert lower.filtration([1, 2]) == 3
    # test that [2, 3] simplex has filtration value 3
    assert lower.filtration([2, 3]) == 3

def test_ladder_length(clf_example):
    assert clf_example.ladder_length == 3

def test_metadata(clf_example):
    assert clf_example.metadata == {'test':[[1,2,3]]}

def test_get_simplicial_complex(clf_example):
    # Test some coordinates from the upper row
    temp = SimplicialComplex()
    temp.from_simplices([(1,),(2,),(3,),(1,2),(2,3),(1,3)])
    assert clf_example.get_simplicial_complex(2, 2) == temp
     # Test some coordinates from the lower row
    temp = SimplicialComplex()
    temp.from_simplices([(1,),(2,),(3,),(1,2),(2,3),(1,3)])
    assert clf_example.get_simplicial_complex(3, 1) == temp
     # Test for an invalid y-coordinate
    with pytest.raises(ValueError):
        clf_example.get_simplicial_complex(1, 3)
    # Test for x-coordinate larger than the ladder length
    with pytest.warns(UserWarning):
        clf_example.get_simplicial_complex(4, 2)

def test_dimension(clf_example):
    assert clf_example.dimension() == {'upper': 2, 'lower': 1}

def test_validation(clf_example):
    # This should not raise an exception
    assert clf_example.validation()






# Assuming the existing fixture clf_example is correctly set up as provided

@pytest.fixture
def clf_resample_example():
    points = np.array([[0.54188618, 0.77381996],
                       [0.25357397, 0.51056493],
                       [0.34719385, 0.38837853],
                       [0.76154592, 0.78689659],
                       [0.73971318, 0.18711194],
                       [0.16215802, 0.07998491]])
    labels = [0] * 6
    indices_removal = [2, 5]
    for i in indices_removal:
        labels[i] = 1
    clf = points_to_clfiltration_chro(pts=points, labels=labels, max_simplex_dim=1+1)
    return clf

def test_resample_filtration(clf_resample_example):
    clf = clf_resample_example
    # Resample filtration with specific indices
    cl3 = clf.resample_filtration(4, [1, 11, 12, 13])
    # Check h_params after resampling
    expected_h_params = [0.0, 0.3000909424289286, 0.3095810970736587, 0.311008537608585]
    np.testing.assert_allclose(cl3.h_params, expected_h_params, atol=1e-12)
    
    # Compute topological invariants after resampling
    inv3 = CLInvariants(cl3)
    inv3.total_decomposition_computation(dim=1, prime=2)
    
    # Check the computed topological invariants
    assert inv3.decompositions_all[0].nonzero_components == {'N9': 1}

# Include your existing tests here


