import itertools

import numpy as np
from einops import *

from typing import *


def quantize(arr: np.ndarray, unit: float = 1) -> np.ndarray:
    """
    Quantiles the values in arr with unit as the step.
    
    Args:
        arr: The array to be quantized.
        unit: The step for quantization.
    
    Returns:
        The quantized array.
    """
    return np.round(arr/unit)*unit


def normalize(arr: np.ndarray, vrange: Tuple[float, float] = (0,1)) -> np.ndarray:
    """
    Normalizes the values in arr with unit in the specified range.
    
    Args:
        arr: The array to be normalized.
        vrange: The range for normalization in (min_final_value, max_final_value).
    
    Returns:
        The normalized array.
    """
    vmin, vmax = vrange
    return (arr-np.min(arr))/(np.max(arr)-np.min(arr))*(vmax-vmin)+vmin


def vec_hash(vec: np.ndarray, seed: float = 0) -> float:
    """
    Generates a seeded "hash" for any dimension of coordinates.
    
    Args:
        vec: The vectors to be hashed, with shape of (..., dimension).
        seed: A float as the seed.
    
    Returns:
        The "hash" result, with the shape of (...). 
    """
    scale_vec = np.arange(vec.shape[-1]) + 227.249 + seed
    return ((vec@scale_vec)**2 * (384567 + seed)) % 1


def perlin_noise_2d(coords: np.ndarray, scale: float = 1, seed: float = 0) -> np.ndarray:
    """
    Generates a seeded 2D Perlin noise at the coordinates.
    
    Args:
        coords: The coordinates, with shape of (..., 2).
        scale: The scale of the noise. Smaller value gives smoother result.
        seed: A float as the seed.
    
    Returns:
        The resulting Perlin noise, with the shape of (...). 
    """
    def fade(t):
        return 6*t**5 - 15*t**4 + 10*t**3
    coords = np.asarray(coords)
    in_shape = coords.shape
    dimension = in_shape[-1]
    coords_flatten = coords.reshape([-1,dimension]).astype(float)
    
    coords_flatten *= scale
    coords_int = np.floor(coords_flatten)
    coords_fract = coords_flatten % 1
    
    fx, fy = fade(coords_fract).T
    result = np.zeros(coords_flatten.shape[:-1], dtype=float)
    
    for dx, dy in itertools.product([0,1],repeat=dimension):
        v = vec_hash(coords_int+(dx,dy), seed=seed)*2-1
        theta = vec_hash(coords_int+(dx,dy), seed=seed+1) *np.pi*2
        
        result += (
            (v + (np.cos(theta)*(fx-dx) + np.sin(theta)*(fy-dy))) 
            * (dx*fx + (1-dx)*(1-fx)) * (dy*fy + (1-dy)*(1-fy))
        )
    
    result = result.reshape(in_shape[:-1])
    return result if in_shape[:-1] else result[()]


def fractal_noise_2d(coords: np.ndarray,
    scale: float = 1, depth: int = 3, detail: float = .5, seed: float = 0) -> np.ndarray:
    """
    Generates a seeded 2D fractal noise at the coordinates by stacking 2D Perlin noises.
    
    Args:
        coords: The coordinates, with shape of (..., 2).
        scale: The scale of the noise. Smaller value gives smoother result.
        depth: The depth of the scale doubling. 
        detail: The amplitude multiplier when doubling the scale. Larger value gives rougher result.
        seed: A float as the seed.
    
    Returns:
        The resulting fractal noise, with the shape of (...). 
    """
    result = perlin_noise_2d(coords, scale, seed)
    for d in range(1, depth):
        result += perlin_noise_2d(coords, scale*(2**d), seed+d) * (detail**d)
    
    return result