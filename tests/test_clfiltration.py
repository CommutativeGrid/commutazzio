from classia.filtration import CLFiltration,SimplicialComplex
from gudhi import SimplexTree
import pytest


@pytest.fixture
def clf_example():
    cc=CLFiltration()
    f2=SimplexTree()
    f1=SimplexTree()
    f2.insert([1,2],1)
    f2.insert([1,2],2)
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


