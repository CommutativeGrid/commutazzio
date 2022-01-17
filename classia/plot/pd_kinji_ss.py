#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 12:21:08 2022

@author: kasumi
"""
import os
import uuid

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from ..helper import create_directory
from .colors_helper import get_color


class CommutativeLadderPdSS():
    """plot persistence diagrams of a commutative ladder
    """

    def __init__(self, dots, lines, title=None, ladder_length=50):
        """acquire data
        """
        self.dots = dots
        self.lines = lines
        self.multi_dots_min = min(dots.multiplicity)
        self.multi_dots_max = max(dots.multiplicity)
        self.data_preprocessing_dots()
        if self.lines.empty is False:
            self.multi_lines_min = min(lines.multiplicity)
            self.multi_lines_max = max(lines.multiplicity)
            self.data_preprocessing_lines()
        self.ladder_length = ladder_length
        self.title = title
        self.legend = True
        self.template='plotly'
        self.size_area_min = 5  # min dot size in area
        self.size_area_max = 24  # max dot size in area
        self.compute_colorscales()

    def render(self,export_mode,**kwargs):
        """Combine scatter and line chart together and generate the final plot
        Parameters
        ----------
        export_mode : str
            'full_html' or 'div
        **kwargs :
            for fig.write_image
        """
        offset = 0.5  # offset to beautify the plot
        offset_diag = 0  # offset for the diagonal line
        fig = go.Figure()  # initiate the final figure
        # add a diagonal line, use add_trace because the layer of add_shape does not work properly
        fig.add_trace(go.Scatter(
            x=[-offset_diag, self.ladder_length+offset_diag],
            y=[-offset_diag, self.ladder_length+offset_diag],
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
        # the layer of shape does not work properly
        # fig.add_shape(type="line",
        #               x0=-offset, y0=-offset,
        #               x1=self.ladder_length+offset, y1=self.ladder_length+offset,
        #               line=dict(
        #                   color="MediumPurple",
        #                   width=4,
        #                   dash="dot",
        #               ),
        #               layer='below',  # draw the diagonal line at the bottom
        #               )
        # create scatter chart and line chart for the final figure
        # https://stackoverflow.com/questions/65124833/plotly-how-to-combine-scatter-and-line-plots-using-plotly-express
        fig1 = self.scatter_chart()
        if self.lines.empty is not True:
            fig2 = self.line_chart()
            fig.add_traces(data=[*fig2.data, *fig1.data])
        else:
            fig.add_traces(data=[*fig1.data])
        # set the plot range of axis and scale ratio
        fig.update_xaxes(
            range=[0-offset, self.ladder_length+offset],
            constrain='domain',
            # fixedrange=True,
        )
        fig.update_yaxes(
            range=[0-offset, self.ladder_length+offset],
            constrain='domain',
            scaleanchor="x",
            scaleratio=1,
            # fixedrange=True,
        )
        # configure the layout
        #https://plotly.com/python/templates/
        fig.update_layout(
            template=self.template,
            #paper_bgcolor='AliceBlue',
            # margin=dict(l=20, r=20, t=20, b=20),  # set up plot size
            margin=dict(l=20, b=20),
            autosize=True,
            # width=1200,
            # height=1200,
            # specify ticks
            # consider about using array mode to
            # specify the tick texts
            xaxis=dict(
                tickmode='linear',
                tick0=0,
                dtick=self.ladder_length/10,
            ),
            yaxis=dict(
                tickmode='linear',
                tick0=0,
                dtick=self.ladder_length/10,
            ),
            # specify the title
            # https://plotly.com/python/figure-labels/
            title=dict(
                text=self.title,
                #y=0.95,
                # x=0.3,
                xanchor='left',  # "auto" | "left" | "center" | "right"
                yanchor='top'  # "auto" | "top" | "middle" | "bottom"
            ),
            xaxis_title='',
            yaxis_title='',
            font=dict(
                family="Rockwell",
                size=22,
            )
        )
        if self.legend:
            fig.update_layout(
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1,
                    xanchor="right",
                    x=0,
                    itemsizing="constant",
                    title_font_family="Times New Roman",
                    font=dict(
                        family="Courier",
                        size=18,
                        #color="black"
                    ),
                    #bgcolor=pio.templates[self.template].layout.plot_bgcolor,
                    bgcolor="WhiteSmoke",
                    bordercolor='black',
                    borderwidth=2,
                ),
                legend_title='',
            )
            

        # fig.show()
        # see https://plotly.com/python/interactive-html-export/
        # for parameters
        dir_name='diagrams'
        create_directory(dir_name)
        if export_mode == 'full_html':
            if 'file' in kwargs:
                file=kwargs.pop('file')
                file=os.path.join(dir_name,file)
            else:
                file=f'./{dir_name}/test.html'
            # check if file already existed
            if os.path.exists(file):
                # change file name (include datetime and some uuid)
                #file=f'./{dir_name}/test_{uuid.uuid4()}.html'
                raise FileExistsError(f'{file} already exists')
            fig.write_html(file=file, include_plotlyjs='cdn')
            print("Saved to", file)
        elif export_mode == 'div':
            if 'file' in kwargs:
                file=kwargs.pop('file')
                file=os.path.join(dir_name,file)
            else:
                file=f'./{dir_name}/div.html'
            if os.path.exists(file):
                # change file name (include datetime and some uuid)
                raise FileExistsError(f'{file} already exists')
            fig.write_html(file=file,full_html=False,include_plotlyjs=False,**kwargs)
            print("Saved to", file)
        else:
            raise ValueError('export_mode should be either full_html or div')
        print("Plot saved to", file)

    def data_preprocessing_dots(self):
        """Add some auxiliary columns to dots
        """
        df = self.dots
        # dot_size_min=10 #obsolete
        # dot_size_max=26
        # avoid 0, which will make the dot be of size 0
        self.dots["log_multi"] = np.log10(df.multiplicity)
        #self.dots["dot_size"] = np.interp(df.log_multi,(min(df.log_multi),max(df.log_multi)),(dot_size_min,dot_size_max))
        self.dots["birth"] = np.where(df.area == 'U', df['x'], df['y'])
        self.dots["death"] = np.where(df.area == 'U', df['y'], df['x'])

    def data_preprocessing_lines(self):
        """Add some auxiliary columns to lines
        """
        df = self.lines
        ribbon_width_coord_min = 0.15
        ribbon_width_coord_max = 0.15
        ribbon_width_pixel_min = 2
        ribbon_width_pixel_max = 8
        self.lines["log_multi"] = df.multiplicity  # np.log10(df.multiplicity)
        # calculate the thickness of the line based on the multiplicity
        self.lines["ribbon_width_coord"] = np.interp(df.log_multi, (min(df.log_multi), max(
            df.log_multi)), (ribbon_width_coord_min, ribbon_width_coord_max))
        self.lines["ribbon_width_pixel"] = np.interp(df.log_multi, (min(df.log_multi), max(
            df.log_multi)), (ribbon_width_pixel_min, ribbon_width_pixel_max))
        # compute the color scale adjusted by the dots' multiplicity
        self.lines["colorscale"] = np.interp(
            df.multiplicity, (self.multi_dots_min, self.multi_dots_max), (0, 1))

    def compute_colorscales(self):
        """Specify the continuous colorscales to be used"""
        #original_colorscales = px.colors.sequential.Plotly3
        original_colorscales = px.colors.sequential.Plasma
        # anchor_point = np.interp(
        #     self.multi_lines_max, (self.multi_dots_min, self.multi_dots_max), (0, 1))
        # values = np.append(np.linspace(
        #     0, anchor_point, len(original_colorscales)-1), 1)
        # self.colorscales = tuple((v, color)
        #                          for v, color in zip(values, original_colorscales))
        self.colorscales = original_colorscales

    def scatter_chart(self):
        """generate the scatter plot, which is a joint of two one-parameter persistence diagrams
        """
        df = self.dots

        color_tick_vals = list(range(0, int(np.log10(self.multi_dots_max))+1))
        color_tick_text = [str(10**i) for i in color_tick_vals]
        # ref on custom_data https://stackoverflow.com/questions/67190756/plotly-scatter-customdata-oare-only-nan
        custom_data = np.stack(
            (df.multiplicity.to_numpy(), df.birth.to_numpy(), df.death.to_numpy()), axis=-1)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['x'],
            y=df['y'],
            customdata=custom_data,
            mode='markers',
            marker=dict(
                size=df.multiplicity,
                sizemode='area',
                # see https://plotly.com/python/bubble-charts/
                sizeref=2.*self.multi_dots_max/(self.size_area_max**2),
                sizemin=self.size_area_min,
                color=df.log_multi,
                colorscale=self.colorscales,
                colorbar=dict(
                    title="multiplicity",
                    titleside="top",
                    tickvals=color_tick_vals,
                    ticktext=color_tick_text,
                ),
                showscale=True,
                opacity=1,
                line=dict(width=0,
                          ),
            ),
            showlegend=False,
            name="",
            hovertemplate="multiplicity:%{customdata[0]}<br>birth:%{customdata[1]}<br>death:%{customdata[2]}",
        )
        )
        # although plotly express is easier, graph object provides more customizability
        # fig = px.scatter(df, x="x", y="y",
        #                  color="multiplicity",
        #                  # opacity=1,
        #                  size="dot_size",
        #                  # hover_name="multiplicity",
        #                  hover_data={
        #                      'x': False,  # remove x from hover data
        #                      'y': False,  # remove y from hover data
        #                      'dot_size': False,  # remove log_multi from hover data
        #                      'multiplicity': True,
        #                      'area': False,
        #                      'birth': True,
        #                      'death': True,
        #                  },
        #                  )

        # hover ref: https://plotly.com/python/hover-text-and-formatting/
        # print("plotly express hovertemplate:", fig.data[0].hovertemplate)
        fig.update_traces(
            # hovertemplate="<b>%{marker.color}</b>", #marker.color is multiplicity
            hoverlabel=dict(
                # bgcolor="#F0F0F0",
                font_size=16,
                font_family="Rockwell"
            ),
            # remove the border
            marker=dict(
                line=dict(width=0,),
            )
        )
        # fig.data[0].marker.color
        #self.colorscales = fig.data[0].marker.colorscale
        return fig

    def line_chart(self):
        """generate the line chart, connect related generators"""
        df = self.lines
        fig = go.Figure()
        exponent_max = int(np.log10(self.multi_lines_max))+1 # +1 for the magnitude containg the max,
        self.separators = [10**i for i in range(0, exponent_max+1)] # another +1 for including the last number
        self.legend_titles=["≤1"]+[f"≤{self.separators[i+1]}" for i in range(0, exponent_max)]
        for index, row in df.iterrows():
            self.add_line(fig, index, row)
        fig.update_traces(
            hoverlabel=dict(
                # bgcolor="#F0F0F0",
                font_size=16,
                font_family="Rockwell"
            )
        )
        return fig

    #https://plotly.com/python/legend/
    def legend_grouping(self, value):
        """group the legend by the multiplicity
        """
        for i, separator in enumerate(self.separators):
            if value <= separator:
                return i
        raise Exception("value is too large")

    def add_line(self, fig, index, row):
        """add a line to the figure"""
        x_coords, y_coords = self.ribbonise(row)
        legend_index = self.legend_grouping(row.multiplicity)
        # add a transparent rectangle for triggering the hover event
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='lines',
            name='',
            fill='toself',
            fillcolor=get_color(self.colorscales, row.colorscale),
            line=dict(  # border line set to zero
                width=0,
            ),
            legendgroup=f"group{legend_index}", # group lines by multiplicity
            showlegend=False,
            text=f"multiplicity:{int(row.multiplicity)}",
            opacity=0,
        ))
        # add the connecting line
        fig.add_trace(go.Scatter(
            x=[row.x0, row.x1],
            y=[row.y0, row.y1],
            mode='lines',
            #name=f"{int(row.multiplicity)}",
            name='',
            line=dict(  # border line
                width=row.ribbon_width_pixel,
                color=get_color(self.colorscales, row.colorscale),
            ),
            legendgroup=f"group{legend_index}",
            legendgrouptitle_text=self.legend_titles[legend_index],
            legendrank=legend_index,
            showlegend=self.legend,
            opacity=0.6,
        ))

    def ribbonise(self, row):
        """Expanding a line to a rectangle
        """
        (x0, y0) = row.x0, row.y0
        (x1, y1) = row.x1, row.y1
        directional_vector = np.array(
            [x1-x0, y1-y0])/np.linalg.norm([x1-x0, y1-y0])
        normal_vector = np.array(
            [-directional_vector[1], directional_vector[0]])
        half_width = row.ribbon_width_coord/2
        (x_a, y_a) = (x0, y0)-half_width*normal_vector
        (x_b, y_b) = (x0, y0)+half_width*normal_vector
        (x_c, y_c) = (x1, y1)+half_width*normal_vector
        (x_d, y_d) = (x1, y1)-half_width*normal_vector
        x_coords = [x_a, x_b, x_c, x_d, x_a]
        y_coords = [y_a, y_b, y_c, y_d, y_a]
        return x_coords, y_coords

if __name__ == "__main__":
    dots = pd.read_pickle("./sample/dots.pkl")
    dots = dots.astype({
        'x': 'int',
        'y': 'int',
        'multiplicity': 'int',
        'area': 'str'
    })
    lines = pd.read_pickle("./sample/lines.pkl")
    lines = lines.astype('int', copy=False)
    aaa = commutative_ladder_pd_ss(dots, lines, title='CL(50)のss方式による区間近似(hcp)')
    aaa.render(export_mode='full_html')
