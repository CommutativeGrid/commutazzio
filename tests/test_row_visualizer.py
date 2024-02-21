import pytest
import numpy as np
from commutazzio.plot.row_visualizer import RowVisualizer  # Adjust the import according to your project structure
import plotly.graph_objects as go

# Provided sample data and weight function
points = np.array([
    [0, 0],
    [1, 0],
    [0.5, np.sqrt(3)/2],
    [3/2, np.sqrt(3)/2],
])

weight_function = {
    (0, 1, 2, 3): 1,
    (0, 1, 2): 0.577,
    (0, 1, 3): 1,
    (1, 2, 3): 0.577,
    (0, 2, 3): 1,
    (0, 1): 0.5,
    (1, 2): 0.5,
    (0, 3): 0.5,
    (2, 3): 0.5,
    (0, 2): 0.5,
    (1, 3): 0.5,
    (1,): 0,
    (2,): 0,
    (0,): 0,
    (3,): 0
}

@pytest.fixture
def row_visualizer():
    return RowVisualizer(points, weight_function)

def test_initialization():
    # Test successful initialization
    rv = RowVisualizer(points, weight_function)
    assert isinstance(rv, RowVisualizer)

def test_get_edges(row_visualizer):
    edges = row_visualizer.get_edges(0.5)
    assert len(edges) == 6  # 5 edges with filtration value <= 0.5
    expected_edges = {(0, 1), (1, 2), (0,3), (2, 3), (0, 2), (1, 3)}
    assert all(tuple(edge) in expected_edges for edge in edges)

def test_get_triangles(row_visualizer):
    triangles = row_visualizer.get_triangles(0.6)
    assert len(triangles) == 2  # 2 triangles with filtration value <= 0.6
    expected_triangles = {(0, 1, 2), (1, 2, 3)}
    assert all(tuple(triangle) in expected_triangles for triangle in triangles)

def test_plot_points(row_visualizer):
    fig = row_visualizer.plot_points()
    assert isinstance(fig, go.Scatter)
    assert len(fig.x) == len(points)  # Ensure all points are plotted

def test_plot_edges(row_visualizer):
    fig = row_visualizer.plot_edges(0.51)
    assert isinstance(fig, go.Scatter)


def test_render_sc(row_visualizer):
    fig = row_visualizer.render_sc(0.6)
    assert isinstance(fig, go.Figure)
    # Expecting points, edges within radius <=0.6, and 2 triangles
    expected_trace_count = 1 + 1 + len(row_visualizer.get_triangles(0.6))
    assert len(fig.data) == expected_trace_count

def test_render_all(row_visualizer):
    radii = [0, 0.5, 0.7]
    fig = row_visualizer.render_all(radii)
    assert isinstance(fig, go.Figure)
    # We expect a trace for the points, edges, and triangles for each radius threshold 
    assert len(fig.data) == 8
