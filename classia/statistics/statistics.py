from .. import Pipeline

def connection_ratio(pipeline_object,version):
    """
    Input has to be a Pipeline object
    Return 2*(number of connections) / (number of nodes)
    as the connection ratio
    """
    assert isinstance(pipeline_object, Pipeline)
    lines,dots=pipeline_object.compute_engine.lines,pipeline_object.compute_engine.dots
    multiplicity_lines=lines["multiplicity"].sum()
    multiplicity_dots=dots["multiplicity"].sum()
    multiplicity_dots_D=dots.loc[dots["area"]=="D"]["multiplicity"].sum()
    if version == 1:
        return 2*multiplicity_lines/multiplicity_dots
    elif version == 2:
        return multiplicity_lines/multiplicity_dots_D