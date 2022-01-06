#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 22:15:51 2022

@author: kasumi
"""
import pickle


def pickle_load(fn):
    with open(fn,"rb") as file:
        var=pickle.load(file)
    return var


if __name__ == '__main__':
    var_names=['fcc','hcp']
    results=[]
    for s in var_names:
        new_result=pickle_load(f"./{s}.pkl")
        results.append(new_result)
    fcc,hcp=results
    
    fcc.plot(title='CL(50)のss方式による区間近似(fcc)',export_mode='full_html',overwrite=True)
    #fcc.plot_js()
    hcp.plot(title='CL(50)のss方式による区間近似(hcp)',export_mode='full_html',overwrite=True)
    #hcp.plot_js()
    