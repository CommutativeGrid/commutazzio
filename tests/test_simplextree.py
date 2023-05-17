import pytest
from commutazzio.filtration import SimplexTree

@pytest.fixture
def setup_simplex_tree():
    st1 = SimplexTree()
    fvs = [0.1, 0.2, 0.3, 0.4]
    st1.insert([0, 1], fvs[0])
    st1.insert([2], fvs[1])
    st1.insert([1, 2, 3], fvs[2])
    st1.insert([4], fvs[3])
    st2 = st1.to_ordinal_number_indexing(fvs)
    st3 = st2.to_custom_filtration_values([1.5, 3.4, 4.6, 9.9])
    st4 = st2.to_custom_filtration_values([1.5, 3.4, 4.6])
    return st1, st2, st3, st4

def test_to_ordinal_number_indexing(setup_simplex_tree):
    st1, st2, _, _ = setup_simplex_tree
    filtration = list(st2.get_filtration())
    assert filtration == [([0], 1.0), ([1], 1.0), ([0, 1], 1.0),([2], 2.0), ([1, 2], 3.0),([3], 3.0),([1, 3], 3.0),([2, 3], 3.0),([1, 2, 3], 3.0),([4], 4.0)]

def test_to_custom_filtration_values(setup_simplex_tree):
    _, _, st3, st4 = setup_simplex_tree
    filtration3 = list(st3.get_filtration())
    filtration4 = list(st4.get_filtration())
    assert str(filtration3) == '[([0], 1.5), ([1], 1.5), ([0, 1], 1.5), ([2], 3.4), ([1, 2], 4.6), ([3], 4.6), ([1, 3], 4.6), ([2, 3], 4.6), ([1, 2, 3], 4.6), ([4], 9.9)]'
    import ast
    assert filtration4 == ast.literal_eval(str(st4))
