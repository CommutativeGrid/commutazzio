#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 23 14:36:04 2021

@author: kasumi
"""

import numpy as np
from .radia_generator import radia_generator


def command_generator(in_fn,out_fn,start=1,end=6,ladder_length=50,executor='./cech_filtration'):
    radia=radia_generator(start,end,ladder_length)
    #output=[executor,str(ladder_length),*[str(np.round(np.sqrt(_),3)) for _ in radia],"<",in_fn,">",out_fn]
    output=[executor,str(ladder_length),*[str(np.round(_,3)) for _ in radia],"<",in_fn,">",out_fn]
    #breakpoint()
    return ' '.join(output)

if __name__ == '__main__':
    fcc_cmd=command_generator('fcc_8.out', 'fcc_8_filt.txt')
    hcp_cmd=command_generator('hcp_8.out', 'hcp_8_filt.txt')
    