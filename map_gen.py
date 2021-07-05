import numpy as np
import scipy as sp
from scipy import signal

from tile_type import Tile_type
import tile

from typing import *


def hill(xx: np.ndarray, yy:np.ndarray, /,
         center: Tuple[float,float]=None, scale: float=None, ar: float=None, *,
         h_order: float=2, d_order: float=2) -> np.ndarray:
    """Generate a hill-shaped height map with max height of 1.
    
    Args:
        xx: Mashgrid x coordinates.
        yy: Mashgrid y coordinates.
        center: Center of the hill. Defaults to the center of the meshgrid.
        scale: The scale of the hill. 
        ar: The aspect ratio (y/x) of the hill.
        h_order: The order of the height curve function.
        d_order: The order of the distance function.
    
    Returns:
        A numpy array containing the height map.
    """
    if center is None:
        center = (np.mean(xx), np.mean(yy))
    if scale is None:
        scale = ((np.max(xx)-np.min(xx))*(np.max(yy)-np.min(yy)))**.5/2
    if ar is None:
        ar = (np.max(xx)-np.min(xx))/(np.max(yy)-np.min(yy))
    cx, cy = center

    ar_fac = ar**.5
    dist = (np.abs((xx-cx)/ar_fac)**d_order +
            np.abs((yy-cy)*ar_fac)**d_order)**(1/d_order)
    return 1/(np.abs(dist/scale)**h_order+1)


def base_map_gen(map_size: Tuple[int, int], seed: Any = None) -> np.ndarray:
    """Generate a numpy array containing tile ID.

    Args:
        map_size: Size of the map in (x, y) format.
        seed: Optional seed for map generation.

    Returns:
        Generated map. 
    """
    if seed is not None:
        np.random.seed(seed)

    xx, yy = np.meshgrid(*(range(i) for i in map_size), indexing='ij')
    heightmap = np.zeros(map_size)
    map_mn = sum(map_size)/2

    # Generates hills.
    for i in range(int(map_mn*.8)):
        hill_size = np.random.uniform(.5, 2)
        scale_fac = 2**np.random.uniform(-1, 1)
        heightmap += hill(xx, yy,
                          center=np.random.uniform(.1, .9, 2)*map_size,
                          scale=hill_size*scale_fac,
                          ar=2**np.random.uniform(-1, 1),
                          h_order=np.clip(np.random.normal(2.5, .5), 1, 5),
                          d_order=np.clip(np.random.normal(2, .2), 1, 5)
                          )*hill_size/scale_fac

    # Generates vallys.
    for i in range(int(map_mn*.5)):
        hill_size = -np.random.uniform(.5, 2)
        scale_fac = 2**np.random.uniform(-1, 1)
        heightmap += hill(xx, yy,
                          center=np.random.uniform(.1, .9, 2)*map_size,
                          scale=hill_size*scale_fac,
                          ar=2**np.random.uniform(-1, 1),
                          h_order=np.clip(np.random.normal(2.5, .5), 1, 5),
                          d_order=np.clip(np.random.normal(2, .2), 1, 5)
                          )*hill_size/scale_fac

    heightmap += np.random.normal(0, .1, map_size)

    
    # Smooth the heightmap for better connectivity in future steps.
    smooth_kernal = np.array(
        [
            [1, 2, 1],
            [2, 4, 2],
            [1, 2, 1],
        ], dtype=float)
    smooth_kernal /= float(np.sum(smooth_kernal))
    heightmap = signal.convolve2d(
        heightmap, smooth_kernal, mode='same', boundary='fill', fillvalue=0)
    heightmap += np.random.normal(0, .1, map_size)

    heightmap -= np.quantile(heightmap, .2)
    max_height = np.max(heightmap)

    boarder_gen = hill(xx, yy, h_order=10, d_order=5)
    base_heightmap = (1 - boarder_gen)*max_height*.5
    heightmap *= boarder_gen
    combined_heightmap = base_heightmap + heightmap

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


def gen_neighbor_value_maps(tile_mask, border=1):
    bitmasks = np.array([
        [0x80, 0x01, 0x10],
        [0x08, 0x00, 0x02],
        [0x40, 0x04, 0x20],
        ])
    return signal.convolve2d(tile_mask, bitmasks, mode='same', boundary='fill', fillvalue=border).astype(int)


def map_replace_tile_ids(tile_id: np.ndarray,
                         replace_map: List[
                            Tuple[int, Optional[Set[int]], Optional[Set[tile.Tile_connectivity]], Dict[int, float]]],
                         seed: Any = None):
    """Replaces id in a tile map array.
    
    Arg:
        tile_id: The original tile map.
        replace_map:
            A replacement table in the following format:
            [(from_id, {connected_id}, {connectivity}, {to_id: weight, ...}), ...]
            If {connected_id} is None, only onnected to the same tile type.
            If {connectivity} is None, ignores connectivity.

    """
    if seed is not None:
        np.random.seed(seed)
    map_size = tile_id.shape

    for tile_type, connected_id, conn, targets  in replace_map:
        mask = tile_id == tile_type
        if connected_id is None:
            mask_connect = tile_id == tile_type
        else:
            connected_id_np = np.array([int(t) for t in connected_id])
            mask_connect = np.isin(tile_id, connected_id_np)
        
        if conn is not None:
            neighbor_map = gen_neighbor_value_maps(mask_connect)
            conn_np = np.array([int(c) for c in conn])
            mask &= np.isin(neighbor_map, conn_np)

        target_sample = np.array([int(t) for t in targets.keys()])
        target_weight = np.array(list(targets.values()), dtype=float)
        target_weight /= np.sum(target_weight)
        target_gen = np.random.choice(target_sample, p=target_weight, size=map_size)

        tile_id = np.where(mask, target_gen, tile_id)
    
    return tile_id
