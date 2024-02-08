#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 11:51:00 2022

@author: kasumi
"""
import numpy as np
import pandas as pd
from .pd_points3d import PD_Points3D
from cpes import FaceCenteredCubic as FCC
from cpes import HexagonalClosePacking as HCP
import plotly.express as px
import plotly.graph_objects as go


def PD_animation(df):
    fig = px.scatter(df, x="birth", y="death",
                     animation_frame="atoms",
                     color="multiplicity", 
                     hover_name="multiplicity",
                     size_max=50, 
                     )
    fig.add_trace(go.Scatter(
        x=[0.9, 8],
        y=[0.9,8],
        mode='lines',
        line=dict(
            color='LightSteelBlue',
            width=4,
            dash='dot'
        ),
        showlegend=False,
        hoverinfo='none',
    )
    )
    fig.update_xaxes(
        range=[0.9,8],
        constrain='domain',
        zeroline=False,  # https://plotly.com/python/axes/#axis-lines-grid-and-zerolines
        # fixedrange=True,
    )
    fig.update_yaxes(
        range=[0.9,8],
        constrain='domain',
        scaleanchor="x",
        scaleratio=1,
        zeroline=False,
        # fixedrange=True,
    )
    fig.update_traces(marker=dict(size=12,
                              line=dict(width=0,
                                        color='DarkSlateGrey')),
                  selector=dict(mode='markers'))
    return fig


if __name__ == '__main__':
    size = 10
    removal = 15
    fcc = FCC(size)
    df = pd.DataFrame()
    for step in range(0, 30):
        pdiagram = PD_Points3D(fcc,method="alpha")
        new_data = pd.DataFrame(pdiagram.diagram_1_r)
        new_data['atoms'] = size**3-step*removal
        df = df.append(new_data, ignore_index=True)
        if new_data.loc[new_data[0]-0.001>new_data[1]].empty is False:
            breakpoint()
        fcc.thinning(number_removal=removal, mode="singlet", inplace=True)
        # track generators, animation_group
    df.rename(columns={0: 'birth', 1: 'death', 2: 'multiplicity'},inplace=True)

    fig = PD_animation(df)

    fig.write_html('PD_animation.html')
