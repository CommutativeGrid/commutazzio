#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 22:15:51 2022

@author: kasumi
"""
from commutazzio.utils import pickle_load,pickle_load_latest


if __name__ == '__main__':
    
    latest_results=pickle_load_latest(2) # load the latest two result, return a generator 
    fcc,hcp=list(latest_results)
    fcc.plot(title='CL(50)のss方式による区間近似(fcc)',export_mode='full_html',file='fcc.html')
    #fcc.plot_js()
    hcp.plot(title='CL(50)のss方式による区間近似(hcp)',export_mode='full_html',file='hcp.html')
    #hcp.plot_js()
    fcc2=pickle_load('./pickles/fcc.pkl')