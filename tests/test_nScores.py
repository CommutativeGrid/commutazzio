import pytest
import random
from commutazzio.statistics import CL4_NIScores, CLN_NIScores

def test_CL4_NIScores():
    Ls = [f"I{_}" for _ in range(1, 56)] + [f"N{_}" for _ in range(1, 22)]
    total_decomp={'I1':2,'I35':1,'N1':1,'N6':2}
    # create a CL4_NIScores object
    test_obj = CL4_NIScores(total_decomp)
    assert test_obj.agg == 34
    assert test_obj.agg_N == 26
    assert round(test_obj.ns_const, 4) == 0.7647
    total_decomp={'I19':3,'I55':3,'N18':1}
    test_obj = CL4_NIScores(total_decomp)
    assert test_obj.ns_const == 0.5
    assert round(test_obj.ns_logistic(0),5) == 0.54615
    assert round(test_obj.ns_logistic(20),5) == 0.99928

# Mathematica
# f[d0_] := 3*1/(1 + Exp[-(1 - d0)])*1 
# + 3*1/(1 + Exp[-(2 - d0)])*2 
# + 1*1/(1 + Exp[-(9 - d0)])*9

def test_CLN_NIScores():
    dots_str = ',x,y,multiplicity,area\n0,1,1,1,U\n1,2,2,1,U\n2,4,4,1,U\n3,6,6,1,U\n4,6,8,1,U\n5,9,6,1,D\n6,7,7,1,U\n7,8,7,1,D\n8,11,11,1,U\n9,12,12,1,U\n'
    lines_str = ',x0,y0,x1,y1,multiplicity\n0,9,6,6,8,1\n1,8,7,6,7,-1\n2,8,7,6,8,1\n3,8,7,7,7,1\n4,9,7,6,7,1\n5,9,7,6,8,-1\n'
    test_obj = CLN_NIScores(dots_str, lines_str)
    assert test_obj.agg_total == 16
    assert test_obj._numerator_numba() == 10
    assert test_obj.ns_c_prime == 0.625