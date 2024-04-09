import pytest
from commutazzio.filtration import SimplexTree  # Adjust the import statement according to your project structure
import numpy as np
from joblib import Parallel, delayed

def generate_random_point_cloud(num_pts, space_dim):
    return np.random.random((num_pts, space_dim))

def create_simplextree(point_cloud, method='cech'):
    simplextree = SimplexTree()
    simplextree.from_point_cloud(point_cloud, method=method)
    return simplextree

@pytest.fixture
def random_point_cloud():
    return generate_random_point_cloud(10, 3)

def test_simplextree_initialization(random_point_cloud):
    simplextree = create_simplextree(random_point_cloud)
    assert simplextree is not None
    # Add more assertions here to validate the state of the simplextree

def test_parallel_simplextree_creation(random_point_cloud):
    num_simplextrees = 4  # Number of simplex trees to create in parallel
    method = 'cech'

    # Create SimplexTrees in parallel
    simplextrees_parallel = Parallel(n_jobs=num_simplextrees)(
        delayed(create_simplextree)(random_point_cloud, method=method)
        for _ in range(num_simplextrees)
    )

    # Create a SimplexTree sequentially for comparison
    simplextree_sequential = create_simplextree(random_point_cloud, method=method)

    # Compare the properties of the simplextrees created in parallel with the sequential one
    # This might include checking the number of simplices, filtration values, etc.
    for simplextree in simplextrees_parallel:
        assert simplextree == simplextree_sequential  # You need to define the equality comparison in your SimplexTree class

    # Further tests could compare specific properties or results of computations done on the simplextrees
