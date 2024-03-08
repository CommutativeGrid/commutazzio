import numpy as np
import pytest
from commutazzio.filtration import CLFiltration,SimplicialComplex, points_to_clfiltration_chro
import chromatic_tda as chro

@pytest.fixture
def input_data():
    points = np.array([[0.54188618, 0.77381996],
                       [0.25357397, 0.51056493],
                       [0.34719385, 0.38837853],
                       [0.76154592, 0.78689659],
                       [0.73971318, 0.18711194],
                       [0.16215802, 0.07998491]])
    labels = [0] * len(points)
    for i in [2, 5]:
        labels[i] = 1
    radii = [0.300092, 0.30958111, 0.311008537608585, 0.5]
    return points, labels, radii

def test_points_to_clfiltration_chro(input_data):
    points, labels, radii = input_data
    max_simplex_dim = 2
    
    chro_alpha = chro.ChromaticAlphaComplex(points, labels)
    expected_weight_function = {
        (0, 2, 3, 4): 0.3374655937362892,
        (0, 1, 2, 4): 0.31900758169767945,
        (1, 2, 4, 5): 0.3674101610298454,
        (2, 4, 5): 0.2943560897981766,
        (0, 1, 4): 0.31900758169767945,
        (0, 2, 4): 0.3095810970736587,
        (0, 3, 4): 0.311008537608585,
        (0, 2, 3): 0.3374655937362892,
        (2, 3, 4): 0.3374655937362892,
        (1, 2, 5): 0.23642980776729144,
        (0, 1, 2): 0.21671577739407696,
        (1, 4, 5): 0.3674101610298454,
        (1, 2, 4): 0.29195597623587205,
        (0, 1): 0.19520959329358337,
        (2, 4): 0.2205559252626627,
        (1, 2): 0.07696459945353841,
        (0, 4): 0.3095810970736587,
        (3, 4): 0.3000909424289286,
        (1, 5): 0.23642980776729144,
        (0, 3): 0.11002431507287888,
        (1, 4): 0.29195597623587205,
        (2, 3): 0.3374655937362892,
        (4, 5): 0.2943560897981766,
        (0, 2): 0.21671577739407696,
        (2, 5): 0.17982274831100575,
        (1,): 0,
        (2,): 0,
        (5,): 0,
        (0,): 0,
        (3,): 0,
        (4,): 0
    }
    
    assert chro_alpha.weight_function() == expected_weight_function
    
    filt = points_to_clfiltration_chro(pts=points, labels=labels, max_simplex_dim= max_simplex_dim,radii= radii)

    assert filt.get_simplicial_complex(1,1).simplices == [(0,), (1,), (3,), (4,), (0, 1), (0, 3), (1, 4), (3, 4)]
    assert filt.get_simplicial_complex(2,2).simplices == [(0,), (1,), (2,), (3,), (4,), (5,), (0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 4), (1, 5), (2, 4), (2, 5), (3, 4), (4, 5), (0, 1, 2), (0, 2, 4), (1, 2, 4), (1, 2, 5), (2, 4, 5)]