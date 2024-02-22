import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import itertools
import chromatic_tda as chro
from .simplicial_complex_2d import SC2DViz


EPSILON=0#1e-10
#POINT_COLOR="darkcyan"
POINT_COLOR="rgba(0,174,239,1)"
#POINT_COLOR="black"
# POINT_SIZE=15
POINT_SIZE=6
#EDGE_COLOR="#ffe476"
EDGE_COLOR="rgba(247,148,29,0.9)"
# EDGE_WIDTH=7
EDGE_WIDTH=2
#TRIANGLE_COLOR="rgba(135,206,250,0.3)"
#TRIANGLE_COLOR="rgba(140,82,255,0.35)"
TRIANGLE_COLOR="rgba(0,174,239,0.35)"
#DISK_COLOR="rgba(135,206,250,0.05)" #rgba(175,238,238,0.2)
DISK_COLOR="rgba(0,174,239,0.05)"
#CIRCUMFERENCE_COLOR="LightSeaGreen"
CIRCUMFERENCE_COLOR="rgba(0,174,239,1)"
# CIRCUMFERENCE_WIDTH=5
CIRCUMFERENCE_WIDTH=2
PAPER_BGCOLOR='rgba(0,0,0,0)'
PLOT_BGCOLOR='rgba(0,0,0,0)'



class CechCL4Viz():
    """
    visualize the 2D configuration of CL(4)-filtration of simplicial complexes formed from a point cloud in 2D use the Cech Complex
    """
    SC2DViz.EDGE_WIDTH=2
    SC2DViz.CIRCUMFERENCE_WIDTH=2
    SC2DViz.POINT_SIZE= 6
    def __init__(self, points:np.array, deletion_list:np.array):
        """
        """
        points=np.array(points)
        if points.shape[1] != 2:
            # check if dimension of point cloud is 2d
            raise ValueError("The point cloud should be a 2d array.")
        points_upper = points
        points_lower = points[[i for i in range(len(points)) if i not in deletion_list]]
        self.viz_upper = SC2DViz(points_upper, sc_type="cech")
        self.viz_lower = SC2DViz(points_lower, sc_type="cech")
    
    def render_all(self,radii:list,xrange:list=[-5,5], yrange:list=[0,5], subtitles:list[str]=None,width=180,height=220):
        num_columns = len(radii)
        if subtitles is None:
            subtitles = [f"Radius: {r:.5f}" for r in radii]
        fig = make_subplots(rows=2, 
                        cols=num_columns,
                        start_cell="top-left",
                        horizontal_spacing=0.05,
                        vertical_spacing=0.05,
                        subplot_titles=subtitles)

        for i, r in enumerate(radii):
            upper_plot = self.viz_upper.render_sc(radius=r)
            for trace in upper_plot.data:
                fig.add_trace(trace, row=1, col=i+1)
            for shape in upper_plot.layout.shapes:
                fig.add_shape(shape, row=1, col=i+1)
            fig.update_xaxes(range=xrange, row=1, col=i+1)
            fig.update_yaxes(range=yrange, row=1, col=i+1, scaleanchor="x"+str(i+1), scaleratio=1)

            lower_plot = self.viz_lower.render_sc(radius=r)
            for trace in lower_plot.data:
                fig.add_trace(trace, row=2, col=i+1)
            for shape in lower_plot.layout.shapes:
                fig.add_shape(shape, row=2, col=i+1)
            fig.update_xaxes(range=xrange, row=2, col=i+1)
            fig.update_yaxes(range=yrange, row=2, col=i+1,scaleanchor="x"+str(i+num_columns+1), scaleratio=1)

        fig.update_layout(
            width=width * num_columns,
            height=height * 2,
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

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False, scaleanchor="x", scaleratio=1)

        return fig
        

class ChroAlphaCL4Viz():
    """
    visualize the 2D configuration of CL(4)-filtration of simplicial complexes formed from a point cloud in 2D use the Chromatic Alpha Complex.
    """
    def __init__(self, points:np.array, deletion_list:np.array):
        """
        """
        points=np.array(points)
        if points.shape[1] != 2:
            # check if dimension of point cloud is 2d
            raise ValueError("The point cloud should be a 2d array.")
        self.points=points
        self.upper_layer_points = points
        labels=[0]*len(points)
        for i in deletion_list:
            labels[i]=1
        self.chro_alpha = chro.ChromaticAlphaComplex(points, labels)
        self.lower_layer_points = points[[i for i,_ in enumerate(labels) if labels[i] == 0]]
        self.lower_layer_points_indices = [i for i, x in enumerate(labels) if x == 0]
        self.figures=[]


    def render_all(self,radii:list,width=170,height=200):
        #self.figures=[]
        num_cols=len(radii)
        num_rows=2
        x_span = np.max(self.points[:,0]) - np.min(self.points[:,0])
        xrange = [np.min(self.points[:,0])-0.1*x_span, np.max(self.points[:,0])+0.1*x_span]
        y_span = np.max(self.points[:,1]) - np.min(self.points[:,1])
        yrange = [np.min(self.points[:,1])-0.1*y_span, np.max(self.points[:,1])+0.1*y_span]

        fig=make_subplots(rows=num_rows,
                        cols=num_cols,
                        start_cell="top-left",
                        subplot_titles=[f"Radius: {r:.6f}" for r in radii],
                        horizontal_spacing = 0.05,
                        vertical_spacing=0.02,
        )
        for i,radius in enumerate(radii):
            subplot=self.render_sc((1+EPSILON)*radius,layer="upper")
            for trace in subplot.data:
                fig.add_trace(trace,row=1,col=i+1)
            fig.update_xaxes(range=xrange, row=1, col=i+1)
            fig.update_yaxes(range=yrange, row=1, col=i+1, scaleanchor="x"+str(i+1), scaleratio=1)
        for i,radius in enumerate(radii):
            subplot=self.render_sc((1+EPSILON)*radius,layer="lower")
            for trace in subplot.data:
                fig.add_trace(trace,row=2,col=i+1)
            fig.update_xaxes(range=xrange, row=2, col=i+1)
            fig.update_yaxes(range=yrange, row=2, col=i+1,scaleanchor="x"+str(i+num_cols+1), scaleratio=1)

        fig.update_layout(
            #autosize=False,
            width=width*num_cols,
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


    def render_sc(self,radius,layer,width=800,height=800):
        """
        Render the simplicial complex.
        """
        fig=go.Figure()

        for tetrahedron in self.get_tetrahedra(radius):
            if layer in ["upper","u"]:
                fig.add_trace(self.plot_tetrathedron(tetrahedron))
            elif layer in ["lower","l"]:
                if all([v in self.lower_layer_points_indices for v in tetrahedron]):
                    fig.add_trace(self.plot_tetrathedron(tetrahedron))
        for triangle in self.get_triangles(radius):
            if layer in ["upper","u"]:
                fig.add_trace(self.plot_triangle(triangle))
            elif layer in ["lower","l"]:
                if all([v in self.lower_layer_points_indices for v in triangle]):
                    fig.add_trace(self.plot_triangle(triangle))
        fig.add_trace(self.plot_edges(radius,layer))
        fig.add_trace(self.plot_points(layer))
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
    
    def get_n_simplices(self,n,radius):
        """
        return all n-simplices with filtration value equal or less than radius
        notice that filtration value in an alpha complex is squared.
        """
        num=n+1 # number of vertices in an n-simplex
        return np.array([k for k,v in self.chro_alpha.weight_function().items() if len(k) == num and v <= radius])

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
    
    def get_tetrahedra(self,radius):
        """
        return all tetrahedra with filtration value equal or less than radius
        notice that filtration value in an alpha complex is squared.
        """
        return self.get_n_simplices(3,radius)

   
    def plot_points(self,layer):
        """
        Plot the point cloud.
        """
        if layer in ["upper","u"]:
            points=self.upper_layer_points
            fig=go.Scatter(x=points[:,0], y=points[:,1], 
                        mode="markers",
                        marker=dict(size=POINT_SIZE,color=POINT_COLOR))
        elif layer in ["lower","l"]:
            points=self.lower_layer_points
            fig=go.Scatter(x=points[:,0], y=points[:,1],
                        mode="markers",
                        marker=dict(size=POINT_SIZE,color=POINT_COLOR))
        return fig


    def plot_edges(self,radius,layer):
        """
        plot all edges with filtration value not greater than radius
        """
        edges = self.get_edges(radius)

        if layer in ["upper","u"]:
            x_coords=[self.points[edge][:,0] for edge in edges]
            y_coords=[self.points[edge][:,1] for edge in edges]
        elif layer in ["lower","l"]:
            x_coords=[]
            y_coords=[]
            for edge in edges:
                # see if both vertices of the edge are in self.lower_layer_points_indices
                if all([v in self.lower_layer_points_indices for v in edge]):
                    x_coords.append(self.points[edge][:,0])
                    y_coords.append(self.points[edge][:,1])

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

    def plot_tetrathedron(self,tetrahedron):
        x_coords=self.points[tetrahedron][:,0]
        y_coords=self.points[tetrahedron][:,1]
        fig = go.Scatter(x=x_coords, y=y_coords, 
                        fill="toself",mode="none",fillcolor="rgba(128, 0, 128, 1.0)")
        return fig

