#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 12:31:20 2021

@author: kasumi
"""
import dionysus as d
import gudhi as gd
import numpy as np


def filtration_g2d(simplex_tree):
    """
    convert a filtration in a simplex tree (format in gudhi) to a filtration in dionysus
    (generator object to dionysus._dionysus.Filtration)
    """
    if type(simplex_tree) is list:
        g_filtration = simplex_tree
    else:
        g_filtration = simplex_tree.get_filtration()
    filt=d.Filtration()
    for vertices,time in g_filtration:
        filt.append(d.Simplex(vertices,time))
    filt.sort()
    return filt

def diagrams_d2g(diagrams)->list[tuple[int,(float,float)]]:
    """
    convert diagrams in dionysus to a diagram in gudhi
    """
    diagrams_gudhi=[]
    for i,dgm in sorted(enumerate(diagrams),reverse=True):
        for p in dgm:
            diagrams_gudhi.append((i,(p.birth,p.death)))
    return diagrams_gudhi

if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    points = np.random.random([100,3])
    filtration = d.fill_rips(points, 2, 4)
    s_complex = gd.AlphaComplex(points=points)
    simplex_tree = s_complex.create_simplex_tree()
    test=filtration_g2d(simplex_tree)
