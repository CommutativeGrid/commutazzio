from commutazzio.filtration import CLFiltration,SimplicialComplex
from gudhi import SimplexTree as gudhi_SimplexTree
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





