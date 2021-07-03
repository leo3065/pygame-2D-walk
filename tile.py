from PIL import Image
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
    def from_neighbor_array(neighbor_array: np.ndarray) -> Tile_connectivity:
        """Creates from a 3*3 array, where truthy neighbor is considered as connected.
        """
        bitmask = np.array([
            [0x80, 0x01, 0x10],
            [0x08, 0x00, 0x02],
            [0x40, 0x04, 0x20],
        ])
        return Tile_connectivity(int(np.sum(neighbor_array, bitmask)))

    def handle_courners(self) -> Tile_connectivity:
        """Returns the connectivity with the connection of corner dropped if not both cardinal directions are connected.
        """
        new_conn = self.value
        if not (new_conn & Tile_connectivity.Up) and (new_conn & Tile_connectivity.Right):
            new_conn &= ~(Tile_connectivity.Up | Tile_connectivity.Right)
        if not (new_conn & Tile_connectivity.Up) and (new_conn & Tile_connectivity.Left):
            new_conn &= ~(Tile_connectivity.Up | Tile_connectivity.Left)
        if not (new_conn & Tile_connectivity.Down) and (new_conn & Tile_connectivity.Right):
            new_conn &= ~(Tile_connectivity.Down | Tile_connectivity.Right)
        if not (new_conn & Tile_connectivity.Down) and (new_conn & Tile_connectivity.Left):
            new_conn &= ~(Tile_connectivity.Down | Tile_connectivity.Left)
        return Tile_connectivity(new_conn)
    
    # Special methods
    def __int__(self):
        return self.value
    
    def __and__(self, other):
        return Tile_connectivity(self.value & int(other))
    
    def __or__(self, other):
        return Tile_connectivity(self.value | int(other))
    
    def __xor__(self, other):
        return Tile_connectivity(self.value ^ int(other))

    def __invert__(self):
        return Tile_connectivity(self.value ^ 0xFF)
    
    def __bool__(self):
        return self.value > 0
    
    def __str__(self):
        name_map = {
            0x01: '↑', 0x02: '→', 0x04: '↓', 0x08: '←',
            0x10: '↗', 0x20: '↘', 0x40: '↙', 0x80: '↖',
        }
        return ''.join(char for dirc, char in name_map.items() if self.value & dirc)

    # Class constants
    Up = Tile_connectivity(1)
    Right = Tile_connectivity(2)
    Down = Tile_connectivity(4)
    Left = Tile_connectivity(8)


class Tile_sheet_loader(object):
    def __init__(self,
                 tile_origins: Dict['str',Tuple[int,int]],
                 tile_size: Tuple):
        self.tile_origins = tile_origins