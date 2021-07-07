import enum

from pygame.math import Vector2
from PIL import Image, ImageOps
import img_util
import numpy as np

from typing import *


class Facing(enum.IntEnum):
    NONE = -1
    DOWN = 0
    DOWN_LEFT = 1
    LEFT = 2
    UP_LEFT = 3
    UP = 4
    UP_RIGHT = 5
    RIGHT = 6
    DOWN_RIGHT = 7

    def mirror_x(self):
        return Facing((8-self)%8)
    
    @staticmethod
    def from_vector(vec: Vector2):
        if len(vec) > 0:
            return Facing(int((vec.as_polar()[1]-90)/45+8.5)%8)
        else:
            return Facing.NONE


class Sprite_sheet_loader(object):
    def __init__(self, 
                 path: str, *,
                 sprite_origin:  Tuple[int,int],
                 sprite_size: Tuple[int,int],
                 sprite_unit: Tuple[int,int],
                 type_offsets: Dict['str',Tuple[int,int]],
                 facing_offsets: Dict[Facing, Tuple[int, int]],
                 use_pixels_for_type_offsets: bool=False,
                 use_pixels_for_facing_offsets: bool=False,
                 transpert_key: Optional[Tuple[int,int,int]]=None,
                 missing_key: Optional[Tuple[int,int,int]]=None):
        self.sheet_image = Image.open(path)
        self.missing_key = missing_key
        if transpert_key is not None:
            self.sheet_image = img_util.pil_image_transperent_key(self.sheet_image, transpert_key)
            if self.missing_key is not None:
                self.missing_key = self.missing_key + (255,)

        self.sprite_origin = Vector2(sprite_origin)
        self.sprite_size = Vector2(sprite_size)
        self.sprite_unit = Vector2(sprite_unit)

        if not use_pixels_for_type_offsets:
            self.type_offsets = {sprite_type: Vector2(offs).elementwise()*self.sprite_unit
                                 for sprite_type, offs in type_offsets.items()}
        else:
            self.type_offsets = {sprite_type: Vector2(offs) for sprite_type, offs in type_offsets.items()}

        if not use_pixels_for_facing_offsets:
            self.facing_offsets = {face: Vector2(offs).elementwise()*self.sprite_unit
                                   for face, offs in facing_offsets.items()}
        else:
            self.facing_offsets = {face: Vector2(offs) for face, offs in facing_offsets.items()}
    
    def get_sprite_img(self,
                       sprite_type, facing: Facing=None, auto_mirror: bool=True):
        is_mirrored = False

        if facing is None:
            facing = Facing.DOWN
        if auto_mirror and facing not in self.facing_offsets:
            facing = facing.mirror_x()
            is_mirrored = True
        
        offset = self.type_offsets[sprite_type] + self.facing_offsets[facing]
        upper_corner = self.sprite_origin + offset
        lower_corner = upper_corner + self.sprite_size
        if self.sheet_image.getpixel((upper_corner.x+1, upper_corner.y+1)) == self.missing_key:
            print('Missing sprite style:', sprite_type, facing)
        img = self.sheet_image.crop((upper_corner.x, upper_corner.y,
                                    lower_corner.x, lower_corner.y))
        if not is_mirrored:
            return img
        else:
            return ImageOps.mirror(img)