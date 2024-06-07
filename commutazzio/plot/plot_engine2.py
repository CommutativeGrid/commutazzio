#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module for visualizing connected persistence diagrams via complementary triangles plots.
This module contains the ComplementaryTrianglesPlot class which provides functionalities
for generating and displaying these plots using Plotly.
"""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

from ..utils import create_directory, filepath_generator
from .colors_helper import get_color
from ..compute import ConnectedPersistenceDiagram

# global variables for the plot
diagonal_line_color="LightSteelBlue"
legend_background_color="WhiteSmoke"
legend_border_color="black"
line_opacity=0.4
#colorscales=px.colors.sequential.Plotly3
#colorscales=px.colors.sequential.Plasma
#original_colorscales = 
#TODO: align to radii function (currently align to the ladder length)

class OverlappingTrianglesPlot():
    """
    A class for visualizing a connected persistence diagram via a complementary triangles plot. 
    This class supports initialization with either a ConnectedPersistenceDiagram instance 
    or custom data in the form of dictionaries.

    Parameters:
    - cPD (ConnectedPersistenceDiagram, optional): The persistence diagram to be visualized.
    - title (str, optional): Title of the plot.
    - convention (str, optional): Convention used for the plot, defaults to "[b,d)", which means inclusive for birth and exclusive for death.
    - kwargs: Additional keyword arguments for custom data initialization.
    """

    def __init__(self,cPD:ConnectedPersistenceDiagram = None,title = None, convention = "[b,d)",**kwargs):
        """
        Initialize the ComplementaryTrianglesPlot instance. 
        """
        self.title = title
        self.legend = True
        self.line_colorscales = px.colors.sequential.YlGn
        self.dot_U_colorscale = px.colors.sequential.Purp
        self.dot_D_colorscale = px.colors.sequential.Blues
        self.template = 'plotly'
        self.size_area_min = 5  # min dot size in area
        self.size_area_max = 24  # max dot size in area
        self.convention = convention
        # if in kwargs there is a ConnectedPersistenceDiagram object, use it
        if isinstance(cPD, ConnectedPersistenceDiagram):
            self._preprocessing(**cPD.plot_data)
        else:
            self._preprocessing(**kwargs)

    def _preprocessing(self,**kwargs):
        """
        parse the data and do some preprocessing
        """
        self.dots = pd.read_csv(StringIO(kwargs.get("dots")),index_col=0)
        # iterate over rows, if the area is D, swap x and y
        self.dots.loc[self.dots["area"]=="D",["x","y"]] = self.dots.loc[self.dots["area"]=="D",["y","x"]].values
        self.lines = pd.read_csv(StringIO(kwargs.get("lines")),index_col=0)
        # swap x0 and y0 for all rows
        self.lines[["x0","y0"]] = self.lines[["y0","x0"]]
        self.radii = kwargs.get("radii")
        self.radii = np.array(self.radii)
        self.ladder_length = kwargs.get("ladder_length", None)
        self.multi_dots_min = min(self.dots.multiplicity,default=0)
        self.multi_dots_max = max(self.dots.multiplicity,default=0)
        self.data_preprocessing_dots()
        if self.lines.empty is False:
            self.multi_lines_min = min(self.lines.multiplicity)
            self.multi_lines_max = max(self.lines.multiplicity)
            self.data_preprocessing_lines()
        if self.convention == "[b,d)":
            # add a finite number to the last element used to 
            # represents the infinite radius
            # use only three digits to avoid numerical error
            # must be strictly larger than the last element
            if self.radii[-1]-self.radii[-2] < 0.00001:
                Warning("The last two radii are too close to each other.")
                self.inf_replacement = round(self.radii[-1]+0.00001)
            else:
                self.inf_replacement = round(self.radii[-1]+self.radii[-1]-self.radii[-2],5)
            self.radii = np.append(self.radii,self.inf_replacement)
            # format: x0 y0 x1 y1: d_lower  b_lower  b_upper  d_upper
            #increase x0 by one, y1 by one
            self.lines["x0"] += 1
            self.lines["y1"] += 1
            # for all area == D, x plus one
            # for all area == U, y plus one
            self.dots.loc[self.dots["area"]=="D","x"] += 1
            self.dots.loc[self.dots["area"]=="U","y"] += 1

    def show(self):
        """
        a synonym for render and show
        """
        fig = self.render()
        fig.show()

    
    def render(self):
        """
        Generates and returns a Plotly figure that combines scatter and line charts to visualize 
        the connected persistence diagram via a complementary triangles plot.

        Returns
        -------
        plotly.graph_objects.Figure
            A Plotly figure object representing the final plot. 
        """
        offset = 1.25  # offset to beautify the plot
        offset_diag = 0  # offset for the diagonal line
        fig = go.Figure()  # initiate the final figure
        # add a diagonal line, 
        # use add_trace because the layer of add_shape does not work properly
        fig.add_trace(go.Scatter(
            x=[-offset_diag, self.ladder_length+offset_diag],
            y=[-offset_diag, self.ladder_length+offset_diag],
            mode='lines',
            line=dict(
                color=diagonal_line_color,
                width=4,
                dash='dot'
            ),
            showlegend=False,
            hoverinfo='none',
        )
        )
        # the layer of shape does not work properly, see add_shape_to_fig in obsolete.py
        # create scatter chart and line chart for the final figure
        # https://stackoverflow.com/questions/65124833/plotly-how-to-combine-scatter-and-line-plots-using-plotly-express
        fig1U = self.scatter_chart(area="U",colorscale=self.dot_U_colorscale)
        fig1D = self.scatter_chart(area="D",colorscale=self.dot_D_colorscale)
        if self.lines.empty is not True:
            fig2 = self.line_chart() # connecting lines
            fig.add_traces(data=[*fig2.data, *fig1U.data, *fig1D.data])
        else:
            fig.add_traces(data=[*fig1U.data, *fig1D.data])
        # configure the layout
        self.render_general_layout(fig)
        self.render_axes(fig, offset)
        self.render_ticks(fig)
        if self.legend:
            self.render_legend(fig)
        return fig
        


    def render_general_layout(self, fig):
        # https://plotly.com/python/templates/
        fig.update_layout(
            template=self.template,
            # paper_bgcolor='AliceBlue',
            # margin=dict(l=20, r=20, t=20, b=20),  # set up plot size
            margin=dict(l=20, b=20),
            #autosize=True,
            width=1200,
            height=800,
            # specify the title
            # https://plotly.com/python/figure-labels/
            title=dict(
                text=self.title,
                # y=0.95,
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

    def render_axes(self, fig, offset):
        # set the plot range of axis and scale ratio
        fig.update_xaxes(
            range=[0-offset, self.ladder_length+offset],
            constrain='domain',
            zeroline=False,  # https://plotly.com/python/axes/#axis-lines-grid-and-zerolines
            # fixedrange=True,
        )
        fig.update_yaxes(
            range=[0-offset, self.ladder_length+offset],
            constrain='domain',
            scaleanchor="x",
            scaleratio=1,
            zeroline=False,
            # fixedrange=True,
        )

    def render_ticks(self, fig):
        # specify ticks
        # tick_coords = np.array(range(1, self.ladder_length+1, 1))
        # tick_coords = np.concatenate(([1], tick_coords))  # prepend 1
        tick_coords = np.array(range(1,len(self.radii)+1,1))
        radii_text = [f"{r:.2f}" for r in self.radii[tick_coords-1]]
        radii_text[-1]='+inf '
        # show at most 5 ticks
        if len(tick_coords) > 5:
            jump = len(tick_coords)//5
            tick_coords = tick_coords[::jump]
            radii_text = radii_text[::jump]
        # import pdb; pdb.set_trace()
        # print(radii_text)
        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=tick_coords,
                ticktext=radii_text,
                showticklabels=True,
            ),
            yaxis=dict(
                tickmode='array',
                tickvals=tick_coords,
                ticktext=radii_text,
                showticklabels=True,
            ),
        )

    def render_legend(self, fig):
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=0.95,
                itemsizing="constant",
                title_font_family="Times New Roman",
                font=dict(
                    family="Courier",
                    size=18,
                    # color="black"
                ),
                # bgcolor=pio.templates[self.template].layout.plot_bgcolor,
                bgcolor=legend_background_color,
                bordercolor=legend_border_color,
                borderwidth=2,
            ),
            legend_title='',
        )


    @staticmethod
    def check_cdn_access():
        import requests
        url = 'https://cdn.plot.ly/plotly-2.24.1.min.js'
        response = requests.get(url)
        return response.status_code == 200
    
    def render_and_export_figure(self, export_mode="full_html", **kwargs):
        """
        Render the figure and export it based on the specified mode.

        Parameters
        ----------
        export_mode : str
            The mode to export the figure. Options are 'full_html' or 'div'.
        **kwargs : dict
            Keyword arguments for the figure rendering and exporting.
            see https://plotly.com/python/interactive-html-export/ for parameters

        Returns
        -------
        filepath : str
        """
        # Render the figure
        fig = self.render()

        # Define the directory name for saving figures
        dir_name = 'diagrams'
        create_directory(dir_name)
        overwrite = kwargs.pop('overwrite', False)

        # Handle the export based on the mode
        if export_mode in ['full_html', 'div']:
            # default filename set to 'cPD'
            filename = kwargs.pop('filename', 'cPD')
            extension = 'html'
            filepath = filepath_generator(dir_name, filename, extension, overwrite=overwrite)
            # Handle different export modes
            if export_mode == 'full_html':
                include_plotlyjs = 'cdn' if self.check_cdn_access() else True
                fig.write_html(file=filepath, include_plotlyjs=include_plotlyjs, **kwargs)
            elif export_mode == 'div':
                fig.write_html(file=filepath, full_html=False, include_plotlyjs=False, **kwargs)
            return filepath
        else:
            raise ValueError('export_mode must be "full_html", "div", or "object"')


    def data_preprocessing_dots(self):
        """Add auxiliary columns to dots
        """
        df = self.dots # temp df
        # dot_size_min=10 #obsolete
        # dot_size_max=26
        # avoid 0, which will make the dot be of size 0
        self.dots["log_abs_multi"] = np.log10(np.abs(df.multiplicity)) 
        # TODO: WARNING!! 
        # df.multiplicity can be negative, which causes NaN in log10.
        #self.dots["dot_size"] = np.interp(df.log_abs_multi,(min(df.log_abs_multi),max(df.log_abs_multi)),(dot_size_min,dot_size_max))
        self.dots["birth_num"] = np.where(df.area == 'U', df['x'], df['y'])
        self.dots["death_num"] = np.where(df.area == 'U', df['y'], df['x'])
        self.dots["birth_radius"] = np.where(
            df.area == 'U', self.radii[df['x']-1], self.radii[df['y']-1])
        self.dots["death_radius"] = np.where(
            df.area == 'U', self.radii[df['y']-1], self.radii[df['x']-1])
        # self.dots["colorscale"] =  np.interp(
        #     df.log_abs_multi, (np.log10(self.multi_dots_min)
        #     , np.log10(self.multi_dots_max)), (0, 1))

    def data_preprocessing_lines(self):
        """Add auxiliary columns to lines
        """
        df = self.lines
        ribbon_width_coord_min = 0.15
        ribbon_width_coord_max = 0.15
        ribbon_width_pixel_min = 2
        ribbon_width_pixel_max = 8
        self.lines["log_abs_multi"] = np.log10(np.abs(df.multiplicity))
        #TODO: WARNING!!
        # calculate the thickness of the line based on the multiplicity
        self.lines["ribbon_width_coord"] = np.interp(df.log_abs_multi, (min(df.log_abs_multi), max(
            df.log_abs_multi)), (ribbon_width_coord_min, ribbon_width_coord_max))
        self.lines["ribbon_width_pixel"] = np.interp(df.log_abs_multi, (min(df.log_abs_multi), max(
            df.log_abs_multi)), (ribbon_width_pixel_min, ribbon_width_pixel_max))
        # compute the color scale adjusted by the dots' multiplicity
        self.lines["colorscale"] = np.interp(
            df.log_abs_multi, (np.log10(self.multi_dots_min)
            , np.log10(self.multi_dots_max)), (0, 1))

    def scatter_chart(self,area:str,colorscale):
        """generate the scatter plot, which is a joint of two one-parameter persistence diagrams
        """
        df = self.dots[self.dots["area"] == area]
        if self.multi_dots_max <= 1:
            color_tick_vals = [0, 1]
        else:
            color_tick_vals = list(range(0, int(np.log10(self.multi_dots_max))+1))
        color_tick_text = [str(10**i) for i in color_tick_vals]
        # ref on custom_data https://stackoverflow.com/questions/67190756/plotly-scatter-customdata-oare-only-nan
        pre_custom_data = np.stack(
            (df.multiplicity.to_numpy(),
            df.birth_num.to_numpy(),
            df.death_num.to_numpy(),
            df.birth_radius.to_numpy(),
            df.death_radius.to_numpy()),
            axis=-1)
        # change to string according to 
        # {pre_customdata[0]} {pre_customdata[1]:.d} {pre_customdata[3]:.3f} {pre_customdata[2]:.d} {pre_customdata[4]:.3f}
        # if not np.inf, otherwise '\u221E'
        custom_data = []
        for row in pre_custom_data:
            new_row = []
            new_row.append(f"{row[0]:.0f}") # multiplicity
            new_row.append(f"{row[1]:.0f}") # birth_num
            new_row.append(f"{row[2]:.0f}") # death_num
            new_row.append(f"{row[3]:.3f}" if row[3] != self.inf_replacement else ' +\u221E') # birth_radius
            new_row.append(f"{row[4]:.3f}" if row[4] != self.inf_replacement else ' +\u221E') # death_radius
            custom_data.append(new_row)
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
                color=df.log_abs_multi,#get_color(self.colorscales, df.colorscale),#df.log_abs_multi,
                colorscale=colorscale,
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
            showlegend=True,
            name="",
            hovertemplate="multiplicity: %{customdata[0]}<br>"
            +"birth: %{customdata[1]},%{customdata[3]}<br>"
            +"death: %{customdata[2]},%{customdata[4]}",
            # hovertemplate="multiplicity: %{customdata[0]}<br>"
            # +"birth: %{customdata[1]:.d},%{customdata[3]:.3f}<br>"
            # +"death: %{customdata[2]:.d},%{customdata[4]:.3f}",
        )
        )
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
        return fig

    @staticmethod
    def one_legend_in_each_group():
        """An iterator that yields True if the sent value not in container,
        else yields False
        """
        seen = set()
        received = yield 'initialization'
        while True:
            index = index if received is None else received
            if index not in seen:
                seen.add(index)
                received = yield True
            else:
                received = yield False

    def line_chart(self):
        """generate the line chart, connect related generators"""
        df = self.lines
        fig = go.Figure()
        # +1 for the magnitude containg the max,
        exponent_max = int(np.log10(self.multi_lines_max))+1
        # another +1 for including the last number
        self.separators = [10**i for i in range(0, exponent_max+1)]
        
        self.legend_titles = ["[0,1]"]
        self.legend_titles.extend([f"({self.separators[i]},{self.separators[i+1]}]" for i in range(len(self.separators)-1)])
        self.legend_tracker = self.one_legend_in_each_group()
        next(self.legend_tracker)
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

    # https://plotly.com/python/legend/
    def legend_grouping(self, value):
        """group the legend by the multiplicity
        """
        for i, separator in enumerate(self.separators):
            if value <= separator:
                return i
        raise Exception("value is too large")

    def add_line(self, fig, index, row):
        """add a line connecting two dots from two PDs respectively"""
        x_coords, y_coords = self.ribbonise(row)
        legend_index = self.legend_grouping(row.multiplicity)
        fillcolor = get_color(self.line_colorscales, row.colorscale)
        # add a transparent rectangle for triggering the hover event
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='lines',
            name='',
            fill='toself',
            fillcolor=fillcolor, #not used
            line=dict(  # border line set to zero
                width=0,
            ),
            legendgroup=f"group{legend_index}",  # group lines by multiplicity
            showlegend=False,
            text=f"multiplicity:{int(row.multiplicity)}",
            opacity=0,
        ))
        # add the connecting line
        fig.add_trace(go.Scatter(
            x=[row.x0, row.x1],
            y=[row.y0, row.y1],
            mode='lines',
            # name=f"{int(row.multiplicity)}",
            name='',
            line=dict(  # border line
                width=row.ribbon_width_pixel,
                color=fillcolor,
            ),
            legendgroup=f"group{legend_index}",
            legendgrouptitle_text=self.legend_titles[legend_index],
            legendrank=legend_index,
            showlegend=self.legend and self.legend_tracker.send(legend_index),
            opacity=line_opacity,
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

