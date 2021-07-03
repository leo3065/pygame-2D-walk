from pygame.math import Vector2
from PIL import Image
import img_util
import numpy as np

from typing import *


class Tile_connectivity(object):
    """Class for tile connectivy.
    
    The numerial representation uses the following bitmask:
        0x80 0x01 0x10
        0x08 (  ) 0x02
        0x40 0x04 0x20
    """
    def __init__(self, value: int):
        self.value = value & 0xFF
    
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

    def handle_courners(self):
        """Returns the connectivity with the connection of corner dropped if not both cardinal directions are connected.
        """
        new_conn = self.value
        if not (bool(new_conn & Tile_connectivity.Up()) and bool(new_conn & Tile_connectivity.Right())):
            new_conn &= ~Tile_connectivity.from_dpad([9])
        if not (bool(new_conn & Tile_connectivity.Up()) and bool(new_conn & Tile_connectivity.Left())):
            new_conn &= ~Tile_connectivity.from_dpad([7])
        if not (bool(new_conn & Tile_connectivity.Down()) and bool(new_conn & Tile_connectivity.Right())):
            new_conn &= ~Tile_connectivity.from_dpad([3])
        if not (bool(new_conn & Tile_connectivity.Down()) and bool(new_conn & Tile_connectivity.Left())):
            new_conn &= ~Tile_connectivity.from_dpad([1])
        return Tile_connectivity(int(new_conn))
    
    # Special methods
    def __int__(self):
        return self.value
    
    def __and__(self, other):
        return Tile_connectivity(self.value & int(other))
    
    def __rand__(self, other):
        return Tile_connectivity(self.value & int(other))
    
    def __or__(self, other):
        return Tile_connectivity(self.value | int(other))
    
    def __ror__(self, other):
        return Tile_connectivity(self.value | int(other))
    
    def __xor__(self, other):
        return Tile_connectivity(self.value ^ int(other))
    
    def __rxor__(self, other):
        return Tile_connectivity(self.value ^ int(other))

    def __invert__(self):
        return Tile_connectivity(self.value ^ 0xFF)
    
    def __bool__(self):
        return (self.value != 0)
    
    def __repr__(self):
        return f'<Tile_connectivity({self.value:b})>'
    
    def __str__(self):
        name_map = {
            0x01: '↑', 0x02: '→', 0x04: '↓', 0x08: '←',
            0x10: '↗', 0x20: '↘', 0x40: '↙', 0x80: '↖',
        }
        return ''.join(char for dirc, char in name_map.items() if self.value & dirc)
    
    def __hash__(self):
        return hash(('Tile_connectivity', self.value))
    
    def __eq__(self, other):
        if not isinstance(other, Tile_connectivity):
            return False
        return self.value == other.value

    # constants
    @staticmethod
    def Up(): return Tile_connectivity(1)
    
    @staticmethod
    def Right(): return Tile_connectivity(2)
    
    @staticmethod
    def Down(): return Tile_connectivity(4)
    
    @staticmethod
    def Left(): return Tile_connectivity(8)


class Tile_sheet_loader(object):
    def __init__(self, 
                 path: str, *,
                 tile_origin:  Tuple[int,int],
                 tile_size: Tuple[int,int],
                 tile_unit: Tuple[int,int],
                 type_offsets: Dict['str',Tuple[int,int]],
                 connectiviy_offsets: Dict[Tile_connectivity, Tuple[int, int]],
                 use_tiles_for_type_offsets: bool=True,
                 use_tiles_for_connectiviy_offsets: bool=True,
                 transpert_key: Optional[Tuple[int,int,int]]=None):
        self.sheet_image = Image.open(path)
        if transpert_key is not None:
            self.sheet_image = img_util.pil_image_transperent_key(self.sheet_image, transpert_key)

        self.tile_origin = Vector2(tile_origin)
        self.tile_size = Vector2(tile_size)
        self.tile_unit = Vector2(tile_unit)

        if use_tiles_for_type_offsets:
            self.type_offsets = {tile_type: Vector2(offs).elementwise()*self.tile_unit
                                 for tile_type, offs in type_offsets.items()}
        else:
            self.type_offsets = {tile_type: Vector2(offs) for tile_type, offs in type_offsets.items()}

        if use_tiles_for_connectiviy_offsets:
            self.connectiviy_offsets = {conn: Vector2(offs).elementwise()*self.tile_unit
                                        for conn, offs in connectiviy_offsets.items()}
        else:
            self.connectiviy_offsets = {conn: Vector2(offs) for conn, offs in connectiviy_offsets.items()}
    
    def tile_sprite(self,
                    tile_type: str, connectivity: Tile_connectivity=None, handles_corners: bool=True):
        if connectivity is None:
            connectivity = Tile_connectivity(0xFF)
        if handles_corners:
            connectivity = connectivity.handle_courners()
        offset = self.type_offsets[tile_type] + self.connectiviy_offsets[connectivity]
        upper_corner = self.tile_origin + offset
        lower_corner = upper_corner + self.tile_size
        return self.sheet_image.crop((upper_corner.x, upper_corner.y,
                                      lower_corner.x, lower_corner.y))