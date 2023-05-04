import numpy as np
from commutazzio.filtration import pointCloud2Filtration
from commutazzio.compute import CommutativeLadderQuiver as CL4

pts=np.array([[0.94677524, 0.96718804],
       [0.76039062, 0.19894666],
       [0.06017049, 0.3325324 ],
       [0.28360163, 0.98200375],
       [0.82325632, 0.37358189],
       [0.61604513, 0.85897228]])
radii=[0.17399216,0.35642443,0.38279749,0.38289977]

# define test function for pointCloud2Filtration
def test_point_cloud_filtration():
    # create a filtration object from point cloud and radii
    cl4f=pointCloud2Filtration(pts=pts,vertical_removal_input=[3],radii=radii,max_simplex_dim=2)
    # assert that the number of simplices in the upper and lower filtration
    # is as expected
    assert len(cl4f.upper.maximum_simplices) == 22
    assert len(cl4f.lower.maximum_simplices) == 16
    
    # assert that the filtration parameters are as expected
    assert cl4f.h_params == [0.17399216, 0.35642443, 0.38279749, 0.38289977]


# define test function for CommutativeLadder
def test_commutative_ladder():
    # create a filtration object from point cloud and radii
    cl4f=pointCloud2Filtration(pts,[3],radii,2)
    
    # create a CommutativeLadder object with max dimension 4
    cl_engine=CL4(4)
    
    # create upper and lower filtration sequences from the filtration object
    uuu=[cl4f.get_simplicial_complex(*(x,2)) for x in [1,2,3,4]]
    lll=[cl4f.get_simplicial_complex(*(x,1)) for x in [1,2,3,4]]

    # set the filtration sequences in the CommutativeLadder object
    cl_engine.filtration_input(uuu,lll)
    
    # plot the CommutativeLadder object
    cl_engine.plot()
    
    # compute multiplicity of degree-1 generators
    cl_engine.multiplicity_computation(dim=1)
    
    # assert that the output of the multiplicity computation is as expected
    assert cl_engine.decomp_collection[0].nonzero_components == {'N1': 1}
