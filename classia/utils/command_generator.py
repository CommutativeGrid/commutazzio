#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 23 14:36:04 2021

@author: kasumi
"""

import numpy as np


def command_generator(pointcloud_filename,filtration_filename,radii,executor='./cech_filtration'):
    #radii=radii_generator(start,end,ladder_length)
    #output=[executor,str(ladder_length),*[str(np.round(np.sqrt(_),3)) for _ in radii],"<",in_fn,">",out_fn]
    ladder_length=len(radii)
    #print("Ladder length is {ladder_length}.")
    output=[executor,str(ladder_length),*[str(np.round(_,3)) for _ in radii],"<",pointcloud_filename,">",filtration_filename]
    #breakpoint()
    return ' '.join(output)

if __name__ == '__main__':
    from classia.utils import radii_generator
    radii=radii_generator(1,6,50)
    fcc_cmd=command_generator('fcc_8.out','fcc_8_filt.txt', radii=radii_generator(1,6,50),)
    hcp_cmd=command_generator('hcp_8.out','hcp_8_filt.txt', radii=radii_generator(1,6,50),)
    