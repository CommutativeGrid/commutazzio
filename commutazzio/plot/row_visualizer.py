import numpy as np
import gudhi
from gtda.externals import CechComplex
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import itertools


EPSILON=0#1e-10
NUM_COLS=3
#POINT_COLOR="darkcyan"
POINT_COLOR="rgba(0,174,239,1)"
#POINT_COLOR="black"
POINT_SIZE=15
#EDGE_COLOR="#ffe476"
EDGE_COLOR="rgba(247,148,29,0.9)"
EDGE_WIDTH=7
#TRIANGLE_COLOR="rgba(135,206,250,0.3)"
#TRIANGLE_COLOR="rgba(140,82,255,0.35)"
TRIANGLE_COLOR="rgba(0,174,239,0.35)"
#DISK_COLOR="rgba(135,206,250,0.05)" #rgba(175,238,238,0.2)
DISK_COLOR="rgba(0,174,239,0.05)"
#CIRCUMFERENCE_COLOR="LightSeaGreen"
CIRCUMFERENCE_COLOR="rgba(0,174,239,1)"
CIRCUMFERENCE_WIDTH=5
PAPER_BGCOLOR='rgba(0,0,0,0)'
PLOT_BGCOLOR='rgba(0,0,0,0)'


class RowVisualizer():
    def __init__(self, points:np.array, weight_function:dict):
        self.points=np.array(points)
        if points.shape[1] != 2:
            # check if dimension of point cloud is 2d
            raise ValueError("The point cloud should be a 2d array.")
        self.weight_function=weight_function
        self.figures=[]

    def get_n_simplices(self,n,radius):
        """
        return all n-simplices with filtration value equal or less than radius
        notice that filtration value in an alpha complex is squared.
        """
        num=n+1 # number of vertices in an n-simplex
        return np.array([k for k,v in self.weight_function.items() if len(k) == num and v <= radius])

    def get_edges(self,radius):
        """
        return all edges with filtration value equal or less than radius
        notice that filtration value in an alpha complex is squared.
        """
        return self.get_n_simplices(1,radius)

    def get_triangles(self,radius):
        """
        return all triangles with filtration value equal or less than radius
        notice that filtration value in an alpha complex is squared.
        """
        return self.get_n_simplices(2,radius)
    
    def plot_points(self):
        """
        Plot the point cloud.
        """
        fig=go.Scatter(x=self.points[:,0], y=self.points[:,1], 
                        mode="markers",
                        marker=dict(size=POINT_SIZE,color=POINT_COLOR))
        return fig

    def plot_edges(self,radius):
        """
        plot all edges with filtration value not greater than radius
        """
        edges = self.get_edges(radius)
        x_coords=[self.points[edge][:,0] for edge in edges]
        y_coords=[self.points[edge][:,1] for edge in edges]
        x_coords=[[*pair,None] for pair in x_coords]
        y_coords=[[*pair,None] for pair in y_coords]
        x_coords=list(itertools.chain.from_iterable(x_coords))
        y_coords=list(itertools.chain.from_iterable(y_coords))
        fig = go.Scatter(x=x_coords, y=y_coords, mode="lines",
                        fillcolor="red",line=dict(color=EDGE_COLOR,width=EDGE_WIDTH))
        return fig

    def plot_triangle(self,triangle):
        x_coords=self.points[triangle][:,0]
        y_coords=self.points[triangle][:,1]
        fig = go.Scatter(x=x_coords, y=y_coords, 
                        fill="toself",mode="none",fillcolor=TRIANGLE_COLOR)
        return fig
    
    def render_sc(self,radius,width=800,height=800):
        """
        Render the simplicial complex.
        """
        fig=go.Figure()
        for triangle in self.get_triangles(radius):
            fig.add_trace(self.plot_triangle(triangle))
        fig.add_trace(self.plot_edges(radius))
        fig.add_trace(self.plot_points())
        fig.update_layout(
            showlegend=False,
            paper_bgcolor=PAPER_BGCOLOR,
            plot_bgcolor=PLOT_BGCOLOR,
            hovermode=False,
            width=width,
            height=height,
        )
        #x axis
        fig.update_xaxes(visible=False)
        #y axis    
        fig.update_yaxes(
            visible=False,
            scaleanchor = "x",
            scaleratio = 1,
        )
        if radius not in [f for (f,r) in self.figures]:
            self.figures.append((fig,radius))
        #fig.show()
        return fig
    def render_all(self,radii:list,width=330,height=600):
        #self.figures=[]
        num_cols=len(radii)
        num_rows=1
        fig=make_subplots(rows=num_rows,
                        cols=num_cols,
                        start_cell="top-left",
                        subplot_titles=[f"Radius: {r:.6f}" for r in radii],
                        horizontal_spacing = 0.05,
                        vertical_spacing=0.05,
        )
        for i,radius in enumerate(radii):
            subplot=self.render_sc((1+EPSILON)*radius)
            for trace in subplot.data:
                #print(trace)
                row=i//num_cols+1
                col=i%num_cols+1
                fig.add_trace(trace,
                row=row,
                col=col)

            #self.render_sc((1+Epsilon)*radius)a
        fig.update_layout(
            #autosize=False,
            width=width*NUM_COLS,
            height=height*num_rows,
            showlegend=False,
            paper_bgcolor=PAPER_BGCOLOR,
            plot_bgcolor=PLOT_BGCOLOR,
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="#7f7f7f"
            ),
            hovermode=False
        )
        axis_limit=max(list(map(abs,itertools.chain.from_iterable(self.points))))
        plot_range=1.2*axis_limit
        fig.update_xaxes(visible=False,
        range=[-plot_range,plot_range])
        #y axis    
        fig.update_yaxes(
            visible=False,
            scaleanchor = "x",
            scaleratio = 1,
            range=[-plot_range,plot_range],
        )
        return fig

    
