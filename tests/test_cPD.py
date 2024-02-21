from commutazzio.compute import ConnectedPersistenceDiagram as cPD
from commutazzio.plot import ComplementaryTrianglesPlot as Visualizer1
from commutazzio.utils import filepath_generator, delete_file
import os

def test_commutative_property_of_cPD():
    # Set up test data and directories
    l = 5
    radii = [1.5, 1.731, 1.733, 1.999, 2.001]
    test_dir = os.path.dirname(os.path.abspath(__file__))
    # Load filtration data
    Da = cPD(os.path.join(test_dir, "test_fixtures/X_a.fltr"), ladder_length=l, homology_dim=1, filtration_values=radii, clean_up=True)
    Db = cPD(os.path.join(test_dir, "test_fixtures/X_b.fltr"), ladder_length=l, homology_dim=1, filtration_values=radii, clean_up=True)
    # Check that computations are correct
    assert Da.lines.multiplicity.values[0] == 1
    assert Db.lines.empty
    # Attempt to plot
    Va = Visualizer1(**Da.plot_data)
    Vb = Visualizer1(**Db.plot_data)
    fpa=filepath_generator(dirname=test_dir,extension='html')
    fpb=filepath_generator(dirname=test_dir,extension='html')
    Va.render_and_export_figure(filename=fpa,export_mode='full_html')
    Vb.render_and_export_figure(filename=fpb,export_mode='full_html')
    delete_file(fpa)
    delete_file(fpb)