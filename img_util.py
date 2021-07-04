from typing import *

from PIL import Image
import pygame
import numpy as np


def pil_image_transperent_key(image, key=None):
    if key is None:
        key = np.array([0,0,0])
    key = np.array(key)
    image = image.convert('RGBA')
    image_np = np.array(image, dtype=int)
    
    alpha = np.where(np.sum(abs(image_np[:,:,:3] - key), axis=2) == 0, 0, image_np[:,:,-1])
    image_np[:,:,-1] = alpha 
    return Image.fromarray(np.uint8(image_np))


def pil_color_replace(image, 
                     color_from: List[Tuple[int,...]], color_to: List[Tuple[int,...]]):
    if len(color_from) != len(color_to):
        raise ValueError('from_colors and to_colors must have the same length.')
    image_np = np.array(image, dtype=int)
    color_from = np.array(color_from)
    color_to = np.array(color_to)
    channels = image_np.size[-1]

    mask = np.sum(abs(np.stack([image_np]*2, axis=-2)-color_from), axis=-1) == 0
    return np.einsum('xym,mc->xyc',mask,color_to) + image_np*np.stack([1-np.sum(mask, axis=-1)]*channels, axis=-1)


def pil_image_to_surface(image):
    return pygame.image.fromstring(
        image.tobytes(), image.size, image.mode)