#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 23 14:47:08 2021

@author: kasumi
"""
import os

from cpes import FaceCenteredCubic, HexagonalClosePacking

from .compute import CommutativeLadderKinjiSS
from .helper import attach_level, command_generator, create_directory
from .plot import CommutativeLadderPdSS


class Pipeline():
    def __init__(self,crystal_type,start,end,survival_rates=[0.5,1],dim=1,lattice_layer_size=10,ladder_length=50,executor='./random-cech/cech_filtration'):
        #step 1 - generate point cloud
        if crystal_type=='fcc':
            lattice=FaceCenteredCubic(lattice_layer_size,radius=1)
        elif crystal_type=='hcp':
            lattice=HexagonalClosePacking(lattice_layer_size,radius=1)
        file_name_prefix=f"{crystal_type}_{lattice_layer_size}_{survival_rates[0]}_{survival_rates[1]}_{ladder_length}"
        file_name=f"{file_name_prefix}.xyz"
        create_directory(os.path.join(os.getcwd(),'point_cloud'))
        file_path=os.path.join(os.getcwd(),"point_cloud",file_name)
        attach_level(lattice.data,file_path,survival_rates=survival_rates)
        print(f"An {crystal_type.upper()} lattice with {lattice_layer_size**3} atoms generated.")
        #step 2 - generate filtration
        create_directory(os.path.join(os.getcwd(),'filtration'))
        filt_file_path=os.path.join(os.getcwd(),"filtration",f"{file_name_prefix}.fil")
        os.system(command_generator(file_path,filt_file_path,start=start,end=end,ladder_length=ladder_length,executor=executor))
        print("Cech filtration generated.")
        #step 3 - generate the data for PD
        self.compute_engine=CommutativeLadderKinjiSS(filt_file_path,m=ladder_length,n=2,dim=dim)

    def plot_js(self):
        """plot using javascript canvas
        """
        self.compute_engine.save2js(mode="all")

    def plot(self,**kwargs):
        """plot using plotly python
        """
        if 'title' in kwargs:
            title=kwargs.pop('title')
        else:
            title='test_pipeline'
        if 'export_mode' in kwargs:
            export_mode=kwargs.pop('export_mode')
        else :
            export_mode='full_html'
        plot_engine=CommutativeLadderPdSS(self.compute_engine.dots,self.compute_engine.lines,title=title,ladder_length=self.compute_engine.m)
        plot_engine.render(export_mode=export_mode,**kwargs)

def clean(directory):
    """delete all files in a folder"""
    for file in os.listdir(directory):
        file_path=os.path.join(directory,file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)

def clean_all():
    clean('point_cloud')
    clean('filtration')
