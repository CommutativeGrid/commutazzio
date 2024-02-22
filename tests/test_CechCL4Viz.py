import numpy as np
import pytest
from commutazzio.plot import CechCL4Viz  

# Fixture for point data
@pytest.fixture
def point_data():
    A = np.array((0, 0))
    B = np.array((2 * np.sqrt(3), 0))
    C = np.array((np.sqrt(3), 3))
    D = np.array((np.sqrt(3), 1))
    E = np.array((-np.sqrt(3), 3))
    F = np.array((0, 2))
    points_upper = np.array([A, B, C, E, F])
    deletion_list = [3, 4]
    return points_upper, deletion_list

# Test initialization with valid data
def test_init_valid(point_data):
    points_upper, deletion_list = point_data
    viz = CechCL4Viz(points_upper, deletion_list)
    assert viz is not None  # Simple check to ensure the object is created


# Test the render_all method (basic functionality)
def test_render_all_basic_functionality(point_data):
    points_upper, deletion_list = point_data
    viz = CechCL4Viz(points_upper, deletion_list)
    radii = [0, 1, np.sqrt(3), 2]
    fig = viz.render_all(radii)
    assert fig is not None  # Basic check to ensure something is returned
