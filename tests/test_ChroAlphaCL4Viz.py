import numpy as np
import pytest
from commutazzio.plot import ChroAlphaCL4Viz

# Fixture for point data and labels
@pytest.fixture
def point_data():
    points = np.array([
        [0.54188618, 0.77381996],
        [0.25357397, 0.51056493],
        [0.34719385, 0.38837853],
        [0.76154592, 0.78689659],
        [0.73971318, 0.18711194],
        [0.16215802, 0.07998491]
    ])
    deletion_list = [2, 5]
    return points, deletion_list

# Test initialization with valid data
def test_init_valid(point_data):
    points, deletion_list = point_data
    viz = ChroAlphaCL4Viz(points, deletion_list)
    assert viz is not None  # Simple check to ensure the object is created
    
# Test the render_all method (basic functionality)
def test_render_all_basic_functionality(point_data):
    points, deletion_list = point_data
    radii = [0.300092, 0.30958111, 0.311008537608585, 0.5]
    viz = ChroAlphaCL4Viz(points, deletion_list)
    fig = viz.render_all(radii)
    assert fig is not None  # Basic check to ensure something is returned
