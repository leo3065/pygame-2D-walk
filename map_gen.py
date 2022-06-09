from einops import *
import numpy as np
import scipy as sp
from scipy import signal

import gen_util
import tile

from typing import *


def base_map_gen_fractal(map_size: Tuple[int, int], seed: float = 0) -> np.ndarray:
    """Generate a numpy array for the base map containing tile ID.

    Args:
        map_size: Size of the map in (x, y) format.
        seed: Optional seed for map generation.

    Returns:
        Generated map. 
    """
    coords = rearrange(
        np.meshgrid(*(np.arange(i) for i in map_size), indexing='ij'),
        'd ... -> ... d', d=2)

    heightmap = gen_util.fractal_noise_2d(coords, scale=1/8, detail=.25, seed=seed)
    heightmap += np.random.normal(0, .1, map_size)
    heightmap = gen_util.normalize(heightmap)

    heightmap -= np.quantile(heightmap, .2)
    max_height = np.max(heightmap)
    combined_heightmap = heightmap

    # Use scipy.ndimage.measurements.label for generating map with good connectivity.
    wall_threshold_p = .8
    while wall_threshold_p<.95:
        land_type_threshold = np.quantile(heightmap,[.1,wall_threshold_p])
        land_type = (np.subtract.outer(combined_heightmap, land_type_threshold) * [-1,1]>0)

        land_type[0,:,:] = [0,1]
        land_type[map_size[0]-1,:,:] = [0,1]
        land_type[:,0,:] = [0,1]
        land_type[:,map_size[1]-1,:] = [0,1]

        label, componet_count = sp.ndimage.measurements.label(~land_type[:,:,1])
        main_segment = np.argmax(np.bincount(label.flatten())[1:])+1
        if np.sum(label==main_segment)/np.sum(label!=0)>.99 or np.sum(label!=0)-np.sum(label==main_segment)<=2:
            break
        wall_threshold_p += 0.02

    land_type_id_map = np.array([2,1])
    land_type_id = np.einsum('ijk,k->ij', land_type, land_type_id_map)

    return land_type_id.astype(int)
