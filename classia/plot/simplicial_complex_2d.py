import numpy as np
import gudhi
from gtda.externals import CechComplex
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import itertools




class SC2DViz():
    """
    Plot the simplicial complex of a 2D point cloud.
    """
    EPSILON=1e-6
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

    def __init__(self, points, radius_max=np.inf, sc_type="cech",):
        """
        Initialize the simplicial complex.

        Parameters
        ----------
        points : 2d array
            The point cloud.
        sc_type : str
            The type of simplicial complex. cech or alpha
        """
        if points.shape[1] != 2:
            # check if dimension of point cloud is 2d
            raise ValueError("The point cloud should be a 2d array.")
        self.sc_type = sc_type
        if sc_type == "cech":
            cech_complex = CechComplex(points=points,max_radius=np.inf)
            sc_dim_ceil=2
            self.simplex_tree=cech_complex.create_simplex_tree(max_dimension=sc_dim_ceil)
            self.points=points
        elif sc_type == "alpha":
            alpha_complex = gudhi.AlphaComplex(points=points)
            self.simplex_tree=alpha_complex.create_simplex_tree()
            # The vertices in the output simplex tree are not guaranteed to match the order of the input points. 
            # https://gudhi.inria.fr/python/latest/alpha_complex_ref.html#gudhi.AlphaComplex.get_point
            self.points=np.array([alpha_complex.get_point(i) for i in range(simplex_tree.num_vertices())])
        else:
            raise NotImplementedError("The simplicial complex type is not implemented.")
        print(f"using {sc_type} complex")
        self.figures=[]
        self.radius_max=(1+SC2DViz.EPSILON)*radius_max

    def radii_critical(self):
        self.radii=set(_[1] for _ in self.simplex_tree.get_filtration() if _[1]<self.radius_max)
        self.radii=sorted(self.radii)
        return self.radii

    def render_all(self,width=330,height=600):
        #self.figures=[]
        self.radii_critical()
        total_num=len(self.radii)
        num_cols=SC2DViz.NUM_COLS
        num_rows=int(np.ceil(total_num/num_cols))
        fig=make_subplots(rows=num_rows,
                        cols=num_cols,
                        start_cell="top-left",
                        subplot_titles=[f"Radius: {r:.4f}" for r in self.radii],
                        horizontal_spacing = 0.05,
                        vertical_spacing=0.05,
        )
        for i,radius in enumerate(self.radii_critical()):
            subplot=self.render_sc((1+SC2DViz.EPSILON)*radius)
            for trace in subplot.data:
                #print(trace)
                row=i//num_cols+1
                col=i%num_cols+1
                fig.add_trace(trace,
                row=row,
                col=col)
                # fig.update_xaxes(visible=False,row=row,col=col)
                # #y axis    
                # fig.update_yaxes(
                #     visible=False,
                #     scaleanchor = "x",
                #     scaleratio = 1,
                #     row=row,
                #     col=col,
                # )
            for shape in subplot.layout.shapes:
                fig.add_shape(shape,row=row,col=col)
                # fig.update_xaxes(visible=False,row=row,col=col)
                # #y axis    
                # fig.update_yaxes(
                #     visible=False,
                #     scaleanchor = "x",
                #     scaleratio = 1,
                #     row=row,
                #     col=col,
                # )

            #self.render_sc((1+Epsilon)*radius)a
        fig.update_layout(
            #autosize=False,
            width=width*SC2DViz.NUM_COLS,
            height=height*num_rows,
            showlegend=False,
            paper_bgcolor=SC2DViz.PAPER_BGCOLOR,
            plot_bgcolor=SC2DViz.PLOT_BGCOLOR,
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
        #self.figures.append(fig)
        #fig.show()
        return fig


    def render_sc(self,radius,with_circles=True,width=800,height=800):
        """
        Render the simplicial complex.
        """
        fig=go.Figure()
        if with_circles:
            for point in self.points:
                self.add_circle(fig,point,radius)
        for triangle in self.get_triangles(radius):
            fig.add_trace(self.plot_triangle(triangle))
        #fig.add_trace(self.plot_triangles(radius))
        fig.add_trace(self.plot_edges(radius))
        fig.add_trace(self.plot_points())
        fig.update_layout(
            showlegend=False,
            paper_bgcolor=SC2DViz.PAPER_BGCOLOR,
            plot_bgcolor=SC2DViz.PLOT_BGCOLOR,
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

    def render_circles(self,radius):
        fig=go.Figure()
        for point in self.points:
            self.add_circle(fig,point,radius)
        fig.add_trace(self.plot_points())
        fig.update_layout(
            showlegend=False,
            paper_bgcolor=SC2DViz.PAPER_BGCOLOR,
            plot_bgcolor=SC2DViz.PLOT_BGCOLOR,
            hovermode=False,
            width=800,
            height=800,
        )
        fig.update_xaxes(visible=False)
        #y axis    
        fig.update_yaxes(
            visible=False,
            scaleanchor = "x",
            scaleratio = 1,
        )
        
        return fig

    @staticmethod
    def add_circle(fig,center,radius):
        x0=center[0]-radius
        y0=center[1]-radius
        x1=center[0]+radius
        y1=center[1]+radius
        # used add_shape, will be in .layout.shapes
        # instead of .data
        fig.add_shape(type="circle",
            xref="x", yref="y",
            fillcolor=SC2DViz.DISK_COLOR,
            x0=x0, y0=y0, x1=x1, y1=y1,
            line_color=SC2DViz.CIRCUMFERENCE_COLOR,
            line_width=SC2DViz.CIRCUMFERENCE_WIDTH,
            layer="below"
        )

    def get_points(self):
        return self.points
    
    def get_n_simplices(self,n,radius):
        """
        return all n-simplices with filtration value equal or less than radius
        notice that filtration value in an alpha complex is squared.
        """
        num=n+1 # number of vertices in an n-simplex
        if self.sc_type == "cech":
            return np.array([s[0] for s in self.simplex_tree.get_skeleton(n) if len(s[0]) == num and s[1] <= radius])
        elif self.sc_type == "alpha":
            radius_squared=radius**2
            return np.array([s[0] for s in self.simplex_tree.get_skeleton(n) if len(s[0]) == num and s[1] <= radius_squared])

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
                        marker=dict(size=SC2DViz.POINT_SIZE,color=SC2DViz.POINT_COLOR))
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
                        fillcolor="red",line=dict(color=SC2DViz.EDGE_COLOR,width=SC2DViz.EDGE_WIDTH))
        return fig

    def plot_triangle(self,triangle):
        x_coords=self.points[triangle][:,0]
        y_coords=self.points[triangle][:,1]
        fig = go.Scatter(x=x_coords, y=y_coords, 
                        fill="toself",mode="none",fillcolor=SC2DViz.TRIANGLE_COLOR)
        return fig

    def plot_triangles(self,radius):
        """
        plot all triangles with filtration value not greater than radius

        using this function causes unexpected behaviour when triangles overlap
        """
        triangles = self.get_triangles(radius)
        x_coords=[self.points[triangle][:,0] for triangle in triangles]
        y_coords=[self.points[triangle][:,1] for triangle in triangles]
        x_coords=[[*pair,None] for pair in x_coords]
        y_coords=[[*pair,None] for pair in y_coords]
        x_coords=list(itertools.chain.from_iterable(x_coords))
        y_coords=list(itertools.chain.from_iterable(y_coords))
        fig = go.Scatter(x=x_coords, y=y_coords, 
                        fill="toself",mode="none",fillcolor=SC2DViz.TRIANGLE_COLOR)
        return fig



