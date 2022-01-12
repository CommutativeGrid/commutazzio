#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 19:48:02 2022

@author: kasumi
"""
from classia import Pipeline
import pickle


def pickle_save(var,fn):
    with open(fn,"wb") as file:
        pickle.dump(var,file)
    


if __name__ == '__main__':
    size=7
    length=10
    fcc=Pipeline('fcc',start=1,end=6,survival_rates=[0.5,1],dim=1,lattice_layer_size=size,ladder_length=length,executor='./random-cech/cech_filtration')
    hcp=Pipeline('hcp',start=1,end=6,survival_rates=[0.5,1],dim=1,lattice_layer_size=size,ladder_length=length,executor='./random-cech/cech_filtration')
    
    var_names=['fcc','hcp']
    
    for s in var_names:
        pickle_save(eval(s),f"./{s}.pkl")
    