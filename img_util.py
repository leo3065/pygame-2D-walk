from PIL import Image
import pygame
import numpy as np


def pil_image_transperent_key(image, key=None):
    if key is None:
        key = np.array([0,0,0])
    key = np.array(key)
    image = image.convert('RGBA')
    image_np = np.array(image)
    
    alpha = np.where(np.sum(abs(image_np[:,:,:3].astype(int) - key), axis=2) == 0, 0, image_np[:,:,-1])
    image_np[:,:,-1] = alpha 
    return Image.fromarray(np.uint8(image_np))

def pil_image_to_surface(image):
    return pygame.image.fromstring(
        image.tobytes(), image.size, image.mode)