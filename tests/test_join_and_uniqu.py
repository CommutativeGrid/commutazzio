import numpy as np
import pytest
from commutazzio.random.point_cloud_model import join_and_unique

def test_join_and_unique_basic():
    arr1 = np.array([1.12345, 2.23456])
    arr2 = np.array([2.234, 3.34567])
    expected = np.array([1.12345, 2.234, 2.23456, 3.34567])
    result = join_and_unique(arr1, arr2, precision=3)
    np.testing.assert_array_almost_equal(result, expected)

def test_join_and_unique_with_duplicates():
    arr1 = np.array([1.1111, 2.2222])
    arr2 = np.array([1.111, 3.333])
    expected = np.array([1.1111, 2.2222, 3.333])
    result = join_and_unique(arr1, arr2, precision=3)
    np.testing.assert_array_almost_equal(result, expected)

def test_join_and_unique_empty_arrays():
    arr1 = np.array([])
    arr2 = np.array([])
    expected = np.array([])
    result = join_and_unique(arr1, arr2)
    np.testing.assert_array_equal(result, expected)

def test_join_and_unique_no_rounding_needed():
    arr1 = np.array([1.5, 2.5])
    arr2 = np.array([3.5])
    expected = np.array([1.5, 2.5, 3.5])
    result = join_and_unique(arr1, arr2, precision=1)
    np.testing.assert_array_equal(result, expected)
