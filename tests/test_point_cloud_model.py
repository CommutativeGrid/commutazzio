import pytest
from commutazzio.random import RandomFiltrationPointCloudModel

@pytest.fixture
def default_model():
    """Fixture for creating a model with default settings."""
    return RandomFiltrationPointCloudModel()

@pytest.fixture
def custom_model():
    """Fixture for creating a model with custom settings."""
    return RandomFiltrationPointCloudModel(num_pts=10, space_dim=2, ladder_length_min=4, ladder_length_max=10, enable_multi_processing=True, num_cores=2, verbose=True)

def test_initialization_default_parameters(default_model):
    """Verify default initialization."""
    assert isinstance(default_model, RandomFiltrationPointCloudModel)

def test_initialization_custom_parameters(custom_model):
    """Verify custom initialization parameters are set correctly."""
    assert custom_model.num_pts == 20
    assert custom_model.space_dim == 3
    assert custom_model.ladder_length_min == 4
    assert custom_model.ladder_length_max == 20
    assert custom_model.enable_multi_processing is True
    assert custom_model.num_cores == 2
    assert custom_model.verbose is True

def test_point_cloud_generation(custom_model):
    """Test the generation of the point cloud with expected dimensions."""
    # This assumes `upper_layer_pc` attribute stores the generated upper layer point cloud,
    # and that it's accessible for testing. Adjust the attribute name as necessary.
    assert custom_model.upper_layer_pc.shape == (20, 3)

def test_output_structure(custom_model):
    """Ensure the output structure contains the expected keys and valid data."""
    # Assuming `output` is populated after initialization or a specific method call
    assert 'CL(4)' in custom_model.output and 'CL(n)' in custom_model.output
    # Further checks could validate the data type or content of these keys if applicable

# Additional tests can be designed to check the filtration process, persistence diagram computation,
# and the effects of enabling multiprocessing based on available methods and attributes.
