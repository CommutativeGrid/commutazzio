from operator import itemgetter

import numpy as np
#from cpes import FaceCenteredCubic, HexagonalClosePacking


def attach_level(data:np.array,fn:str,space_dim:int=3,survival_rates:list=[0.5,1])->None:
    """attach levels to the point cloud of atoms

    Parameters
    ----------
    data : np.array
        coordinates of atoms of the specified lattice
    fn : str
        file name of the output
    space_dim : int, optional
        dimension of the space, by default 3
    survival_rates : list
        survival rates of the levels, by default [0.5,1]
        in the order of layer zero, layer one
    """
    l=len(data)
    label_0_len=int(l*survival_rates[0]) # number of points in the lowest level
    label_1_len=int(l*survival_rates[1])-int(l*survival_rates[0]) # number of points newly added in layer 1
    indices=label_0_len*[0]+label_1_len*[1]
    indices=np.array(indices)
    np.random.shuffle(indices)# shuffle the indices
    if survival_rates[-1]!=1:
        data=data[np.random.choice(range(l),size=len(indices),replace=False)]
    temp= [(i,*vec) for i,vec in zip(indices,data)]
    output=sorted(temp, key=itemgetter(0))
    np.savetxt(fn,output,fmt=['%d']+['%.6f']*space_dim,delimiter=' ')
    
if __name__ == '__main__':
    fcc=face_centered_cubic(8,radius=1)
    hcp=hexagonal_close_packing(8,radius=1)
    attach_level(fcc.data, './test.out',survival_rates=[0.1,0.3])
    #attach_level(fcc.data,"random-cech/fcc_8.out")
    #attach_level(hcp.data,"random-cech/hcp_8.out")
# =============================================================================
#     minimal = enumerate(np.random.random([50,3])*5)
#     minimal=[(i,*vec) for i,vec in minimal]
#     np.savetxt("random-cech/minimal.out",minimal,fmt=['%d','%.6f','%.6f','%.6f'],delimiter=' ')
#     
# =============================================================================
