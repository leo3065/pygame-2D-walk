import enum

from pygame.math import Vector2
from PIL import Image
import img_util
import numpy as np

from typing import *


class Tile_connectivity(enum.IntFlag):
    """Class for tile connectivy.
    
    The numerial representation uses the following bitmask:
        0x80 0x01 0x10
        0x08 (  ) 0x02
        0x40 0x04 0x20
    """
    UP = 0x01
    RIGHT = 0x02
    DOWN = 0x04
    LEFT = 0x08
    UP_RIGHT = 0x10
    DOWN_RIGHT = 0x20
    DOWN_LEFT = 0x40
    UP_LEFT = 0x80

    FULL = 0xFF
    
    @staticmethod
    def from_neighbor_array(neighbor_array: np.ndarray):
        """Creates from a 3*3 array, where truthy neighbor is considered as connected.
        """
        bitmasks = np.array([
            [0x80, 0x01, 0x10],
            [0x08, 0x00, 0x02],
            [0x40, 0x04, 0x20],
        ])
        return Tile_connectivity(int(np.sum(neighbor_array*bitmasks)))
    
    @staticmethod
    def from_dpad(dpad):
        """Creates from D-pad list.
        
        The D-pad numbering is as following:
            7 8 9
            4 _ 6
            1 2 3
        """
        bitmasks = [
            0x00,
            0x40, 0x04, 0x20,
            0x08, 0x00, 0x02,
            0x80, 0x01, 0x10,
            ]
        conn = 0
        for dirc in dpad:
            conn |= bitmasks[dirc]
        return Tile_connectivity(conn)
    
    @staticmethod
    def all_connectivity():
        """Returns a set with all possible connections.
        """
        return {Tile_connectivity(c) for c in range(256)}

    def handle_courners(self):
        """Returns the connectivity with the connection of corner dropped if not both cardinal directions are connected.
        """
        new_conn = self
        if not (bool(new_conn & Tile_connectivity.UP) and bool(new_conn & Tile_connectivity.RIGHT)):
            new_conn &= ~Tile_connectivity.UP_RIGHT
        if not (bool(new_conn & Tile_connectivity.UP) and bool(new_conn & Tile_connectivity.LEFT)):
            new_conn &= ~Tile_connectivity.UP_LEFT
        if not (bool(new_conn & Tile_connectivity.DOWN) and bool(new_conn & Tile_connectivity.LEFT)):
            new_conn &= ~Tile_connectivity.DOWN_LEFT
        if not (bool(new_conn & Tile_connectivity.DOWN) and bool(new_conn & Tile_connectivity.RIGHT)):
            new_conn &= ~Tile_connectivity.DOWN_RIGHT
        return Tile_connectivity(int(new_conn))
    
    def __str__(self):
        name_map = {
            0x01: '↑', 0x02: '→', 0x04: '↓', 0x08: '←',
            0x10: '↗', 0x20: '↘', 0x40: '↙', 0x80: '↖',
        }
        return ''.join(char for dirc, char in name_map.items() if self.value & dirc)

class Tile_sheet_loader(object):
    def __init__(self, 
                 path: str, *,
                 tile_origin:  Tuple[int,int],
                 tile_size: Tuple[int,int],
                 tile_unit: Tuple[int,int],
                 type_offsets: Dict[Tuple[str, int],Tuple[int,int]],
                 connectiviy_offsets: Dict[Tile_connectivity, Tuple[int, int]],
                 animated_tile_types: List[str]=None,
                 use_pixels_for_type_offsets: bool=False,
                 use_pixels_for_connectiviy_offsets: bool=False,
                 transpert_key: Optional[Tuple[int,int,int]]=None,
                 missing_key: Optional[Tuple[int,int,int]]=None):
        self.sheet_image = Image.open(path)
        self.missing_key = missing_key
        if transpert_key is not None:
            self.sheet_image = img_util.pil_image_transperent_key(self.sheet_image, transpert_key)
            if self.missing_key is not None:
                self.missing_key = self.missing_key + (255,)

        self.tile_origin = Vector2(tile_origin)
        self.tile_size = Vector2(tile_size)
        self.tile_unit = Vector2(tile_unit)

        if not use_pixels_for_type_offsets:
            self.type_offsets = {tile_type: Vector2(offs).elementwise()*self.tile_unit
                                 for tile_type, offs in type_offsets.items()}
        else:
            self.type_offsets = {tile_type: Vector2(offs) for tile_type, offs in type_offsets.items()}

        if not use_pixels_for_connectiviy_offsets:
            self.connectiviy_offsets = {conn: Vector2(offs).elementwise()*self.tile_unit
                                        for conn, offs in connectiviy_offsets.items()}
        else:
            self.connectiviy_offsets = {conn: Vector2(offs) for conn, offs in connectiviy_offsets.items()}
        
        if animated_tile_types is None:
            animated_tile_types = []
        self.animated_tile_types = animated_tile_types
    
    def get_tile_img(self,
                     tile_name, connectivity: Tile_connectivity=None, tile_style=0, *, 
                     handles_corners: bool=True):
        if connectivity is None:
            connectivity = Tile_connectivity.FULL
        if handles_corners:
            connectivity = connectivity.handle_courners()

        offset = self.type_offsets[(tile_name, tile_style)] + self.connectiviy_offsets[connectivity]
        upper_corner = self.tile_origin + offset
        lower_corner = upper_corner + self.tile_size
        if self.sheet_image.getpixel((upper_corner.x+1, upper_corner.y+1)) == self.missing_key:
            offset = self.type_offsets[(tile_name, 0)] + self.connectiviy_offsets[connectivity]
            upper_corner = self.tile_origin + offset
            lower_corner = upper_corner + self.tile_size
        return self.sheet_image.crop((upper_corner.x, upper_corner.y,
                                      lower_corner.x, lower_corner.y))