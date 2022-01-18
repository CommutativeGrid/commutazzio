def add_shape_to_fig():
    fig.add_shape(type="line",
                  x0=-offset, y0=-offset,
                  x1=self.ladder_length+offset, y1=self.ladder_length+offset,
                  line=dict(
                      color="MediumPurple",
                      width=4,
                      dash="dot",
                  ),
                  layer='below',  # draw the diagonal line at the bottom
                  )