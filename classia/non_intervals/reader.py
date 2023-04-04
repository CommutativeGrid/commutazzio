# statistics on obtained point cloud filtrations

import pandas as pd
import numpy as np
from operator import itemgetter
from ..utils import filepath_generator,create_directory
from ..plot import SC2DViz
from plotly.subplots import make_subplots
from .. import Pipeline
from cachetools import cached
import plotly.graph_objects as go

class NonIntervalCL4():
    """Store info of a point cloud data that has a non-interval"""
    def __init__(self,input):
        self.pt=np.array(input['pt'])
        self.removal=np.array(input['removal'])
        self.radii=np.array(input['radii'])
        self.total_decomp=input['total_decomp']
        self.dim = self.pt.shape[1]
    
    def __repr__(self) -> str:
        return f"NonIntervalCL4(\npt={self.pt.__repr__()},\nremoval={self.removal},\nradii={self.radii.__repr__()},\ntotal_decomp={self.total_decomp})"

    @property
    def upper(self):
        return self.pt

    @property
    def lower(self):
        return self.pt[[_ for _ in range(self.pt.shape[0]) if _ not in self.removal]]

    @property
    def df_repr(self):
        return pd.DataFrame({'dim':self.pt.shape[1],'num_pts_upper':self.pt.shape[0],'num_pts_lower':self.pt.shape[0]-self.removal.shape[0]} | self.total_decomp,index=[0])
    
    def write2file(self,filepath=None,style='homcloud'):
        """
        Write the points in a form that can be read by homcloud
        """
        #TODOs
        # print for 2d arrays
        assert style in ['homcloud']
        create_directory('layered_point_cloud')
        if filepath is None:
            filepath=filepath_generator('./layered_point_cloud',suffix='out')
        def label_rule(i):
            if i in self.removal:
                return 1 # removed, will be added at the first layer
            else:
                return 0 # will be added at the zeroth layer

        if self.dim==2:
            labelled_data = [(label_rule(i), *vec, 1e-5*np.random.random()-2e-5) for i, vec in enumerate(self.pt)]
            # labelled_data = [(label_rule(i), *vec, 0.0) for i, vec in enumerate(self.pt)]
        elif self.dim==3:
            labelled_data = [(label_rule(i), *vec,) for i, vec in enumerate(self.pt)]
        else:
            raise NotImplementedError("dim>3 is not supported yet.")
            
        sorted_result = np.array(sorted(labelled_data, key=itemgetter(0)))
        np.savetxt(
                    filepath,
                    sorted_result,
                    fmt=["%d"] + ["%.6f"] * 3,
                    delimiter=" ",
                )
        #remove the trailing newline
        with open(filepath) as f_input:
            data = f_input.read().rstrip('\n')
        with open(filepath, 'w') as f_output:    
            f_output.write(data)
        print(f"File saved @ {filepath} in homcloud format.")
        return filepath

    @cached(cache={})
    def cPD(self):
        title = ",".join([f"{k}={v}" for k,v in self.total_decomp.items()])
        ladder_length = 4
        radii = 1.000001*self.radii
        # ladder_length = 20
        # radii = np.linspace(self.radii[0],1.1*self.radii[-1],num=ladder_length),
        ppl=Pipeline(layered_point_cloud_fpath=self.write2file(),
                 radii=radii,
                 ladder_length=ladder_length,
                 dim=1,
                 executor="../random-cech/cech_filtration")
        ppl.plot(title=title,export_mode='full_html',file=f'{title}.html',overwrite=False)
        return ppl

    def visualization(self,sub_width,sub_height):
        assert self.dim==2
        num_cols=4
        num_rows=2
        upper_plot=SC2DViz(self.upper)
        lower_plot=SC2DViz(self.lower)
        fig=make_subplots(rows=num_rows,
                        cols=num_cols,
                        start_cell="top-left",
                        subplot_titles=[f"Radius: {r:.4f}" for r in self.radii],
                        horizontal_spacing = 0.05,
                        vertical_spacing=0.05,
                        shared_xaxes=True,
                        shared_yaxes=True,
        )
        fig.update_annotations(xshift=50) # move the subplot titles to the right by a little

        for i,radius in enumerate(self.radii):
            subplot=upper_plot.render_sc((1+SC2DViz.EPSILON)*radius)
            for trace in subplot.data:
                row=1 # upper row, all points exist
                col=i%num_cols+1
                fig.add_trace(trace,
                row=row,
                col=col)
            for shape in subplot.layout.shapes:
                fig.add_shape(shape,row=row,col=col)
        
        for i,radius in enumerate(self.radii):
            subplot=lower_plot.render_sc((1+SC2DViz.EPSILON)*radius)
            for trace in subplot.data:
                row=2 # lower row, some points are removed
                col=i%num_cols+1
                fig.add_trace(trace,
                row=row,
                col=col)
            for shape in subplot.layout.shapes:
                fig.add_shape(shape,row=row,col=col)

        fig.update_layout(
            #autosize=False,
            title={
            'text': ",".join([f"{k}={v}" for k,v in self.total_decomp.items()]),
            'y':0.98,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            width=sub_width*4,
            height=sub_height*2,
            showlegend=False,
            paper_bgcolor=SC2DViz.PAPER_BGCOLOR,
            plot_bgcolor=SC2DViz.PLOT_BGCOLOR,
            font=dict(
                family="Courier New, monospace",
                size=24,
                color="#7f7f7f",
            ),
            hovermode=False,
            # modebar_remove=['zoom','zoomIn','zoomOut']
        )
        
        # axis_limit=max(list(map(abs,itertools.chain.from_iterable(self.points))))
        axis_limit = 1
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
        # config = {
        #     # 'staticPlot': True,
        #     'scrollZoom': False,
        #     }
        # return fig.show(config=config)
        return fig 


class StatisticsNonIntervalsCL4():
    def __init__(self):
        self.container = []
        
    def __getitem__(self, idx):
        return self.container[idx]

    def add_from_line(self, line):
        self.container.append(NonIntervalCL4(line))
    
    def data2df(self):
        columns=['dim','num_pts_upper','num_pts_lower']
        columns.extend([f"N{k}" for k in range(1,22)])
        columns.extend([f"I{k}" for k in range(1,56)])
        self.df_components=pd.DataFrame(columns=columns)
        for row in self.container:
            self.df_components=pd.concat([self.df_components,row.df_repr],axis=0)
        self.df_components.reset_index(inplace=True)
        self.df_components.fillna(0,inplace=True)
    

    
    def bar_plot_plotly(self,data,xaxis_title):
        total_obs = data.sum()
        fig = go.Figure(data=[go.Bar(
                    x=data.index,
                    y=data.values/total_obs,
                    marker_color='steelblue'
            )])
        fig.update_layout(
            title="",
            xaxis=dict(
                title=xaxis_title,
                tickangle=45,
                tickfont=dict(size=17),
                titlefont=dict(size=20,color='black')
            ),
            yaxis=dict(
                title="Frequency",
                titlefont=dict(size=20,color='black')
            ),
            width=800,
            height=500,
            template="plotly_white"
        )
        return fig
        # fig.show()

    # https://community.plotly.com/t/plotly-colours-list/11730/3
    def barchart(self,target="non-intervals"):
        if not hasattr(self,'df_components'):
            print("No dataframe available. Running data2df() first.")
            self.data2df()
        if target=="non-intervals":
            data = self.df_components[[f"N{i}" for i in range(1,22)]].sum()
            fig = self.bar_plot_plotly(data,xaxis_title="Non-intervals")
            # self.df_components[[f"N{i}" for i in range(1,22)]].sum().plot.bar(figsize=(18,6))
        elif target=="intervals":
            data = self.df_components[[f"I{i}" for i in range(1,56)]].sum()
            fig = self.bar_plot_plotly(data,xaxis_title="Intervals")
            # self.df_components[[f"I{i}" for i in range(1,56)]].sum().plot.bar(figsize=(18,6))
        return fig
        # fig.show() 

    def dim_counts(self):
        return self.df_components[['dim']].value_counts()
    
    def __len__(self):
        return len(self.container)

            
