#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 23 14:47:08 2021

@author: kasumi
"""
import os
from cpes import FaceCenteredCubic, HexagonalClosePacking
import numpy as np
from .compute import CommutativeLadderKinjiSS
from .utils import attach_level, command_generator, create_directory, radii_generator, filepath_generator
from .plot import CommutativeLadderPdSS
from tempfile import NamedTemporaryFile


def deco_print(func):
    def wrapper(*args, **kwargs):
        func('--------------------')
        func(*args, **kwargs)
    return wrapper

print=deco_print(print)

class Pipeline():
    def __init__(self, point_cloud_fpath=None, layered_point_cloud_fpath=None, filtration_fpath=None, 
                start=None, end=None, radii = None, survival_rates=[0.5, 1], dim=1, ladder_length=50, 
                executor='./random-cech/cech_filtration',mproc=False):
        parameters = {k: v for k, v in locals().items() if k not in [
            'self', 'executor']}
        # dim is used in parameters
        # step 1 - laminate the given point cloud
        # layered point cloud
        print("Initiating plotting sequence based on the given parameters..")
        if point_cloud_fpath is None and layered_point_cloud_fpath is None:
            if filtration_fpath is None:
                raise ValueError("Input data missing.")
        if point_cloud_fpath is not None and layered_point_cloud_fpath is not None:
            raise ValueError('One and only one path to either point_cloud_fp or layered_point_cloud_fp should be provided.')
        
        filename_prefix = f"layered_{survival_rates[0]}_{survival_rates[1]}_{ladder_length}"
        if point_cloud_fpath is not None:
            try:
                point_cloud = np.load(point_cloud_fpath)
            except ValueError:
                pass
            try:
                point_cloud = np.loadtxt(point_cloud_fpath)
            except Exception as e:
                print(e) 
            create_directory(os.path.join(os.getcwd(), 'layered_point_cloud'))
            layered_filename=os.path.normpath(point_cloud_fpath).split(os.path.sep)[-1]
            layered_filename=''.join(layered_filename.split('.')[:-1])
            layered_point_cloud_fpath = filepath_generator(os.path.join(os.getcwd(), "layered_point_cloud"),f"{filename_prefix}_{layered_filename}","lyr")
            attach_level(point_cloud, layered_point_cloud_fpath, survival_rates=survival_rates)
            print(f"Layered point cloud data {layered_point_cloud_fpath} generated.")
        elif layered_point_cloud_fpath is not None:
            print(f"Layered point cloud data {layered_point_cloud_fpath} received.")
        # step 2 - generate filtration
        if filtration_fpath is None:
            print(f"Starting filtration process..")
            create_directory(os.path.join(os.getcwd(), 'filtration'))
            filtration_fpath = filepath_generator(os.path.join(os.getcwd(), "filtration"),f"{filename_prefix}_filtration","fltr")
            if radii is None:
                radii=radii_generator(start,end,ladder_length)
            os.system(command_generator(layered_point_cloud_fpath, filtration_fpath, radii=radii, executor=executor))
            print("Cech filtration generated.")
        else:
            print(f"Using the input filtration.")
        # step 3 - generate the data for PD
        self.compute_engine = CommutativeLadderKinjiSS(
            txf=filtration_fpath, **parameters)
        print("Computation finished.")
        print("-------------------------------------")
        print("-------------------------------------")

    def plot(self, **kwargs):
        """plot using plotly python
        """
        if 'title' in kwargs:
            title = kwargs.pop('title')
        else:
            title = 'test_pipeline'
        if 'export_mode' in kwargs:
            export_mode = kwargs.pop('export_mode')
        else:
            export_mode = 'full_html'
        # for legacy compatibility
        # will be delete in the next version
        if hasattr(self.compute_engine, 'parameters'):
            plot_engine = CommutativeLadderPdSS(
                title=title, **self.compute_engine.parameters)
        else:
            parameters = dict(dots=self.compute_engine.dots,
                             lines=self.compute_engine.lines,
                             radia=np.array([r for r in radia_generator(1,6,50)]),
                             ladder_length=50)
            plot_engine = CommutativeLadderPdSS(
                title=title, **parameters)

        plot_engine.render(export_mode=export_mode, **kwargs)

class PipelineClosePacking(Pipeline):
    def __init__(self, crystal_type, start=None, end=None, radii = None, survival_rates=[0.5, 1], 
                dim=1, lattice_layer_size=10, ladder_length=50, 
                executor='./random-cech/cech_filtration',mproc=False):
        # parameters = {k: v for k, v in locals().items() if k not in [
        #     'self', 'executor']}
        # step 1 - generate point cloud
        if crystal_type == 'fcc':
            lattice = FaceCenteredCubic(lattice_layer_size, radius=1)
        elif crystal_type == 'hcp':
            lattice = HexagonalClosePacking(lattice_layer_size, radius=1)
        print(
            f"An {crystal_type.upper()} lattice with {lattice_layer_size**3} atoms generated.")
        with  NamedTemporaryFile() as outfile:
            np.savetxt(outfile.name, lattice.data)
            super().__init__(point_cloud_fpath=outfile.name, layered_point_cloud_fpath=None, start=start, end=end, 
            radii = radii, survival_rates=survival_rates, dim=dim, ladder_length=ladder_length, executor=executor,
            mproc=mproc)


    # def plot_js(self):
    #     """plot using javascript canvas
    #     """
    #     self.compute_engine.save2js(mode="all")
