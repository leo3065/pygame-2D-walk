from typing import *

from PIL import Image

class Tile_connectivity(object):
    """Class for tile connectivy.
    
    The numerial representation uses the following bitmask:

        0x80 0x01 0x10
        0x08 (  ) 0x02
        0x40 0x04 0x20

    """
    def __init__(self, value: int):
        self.value = value & 0xFF
    
    def __int__(self):
        return self.value
    
    def __str__(self):
        pass

    # Class constants
    Up = Tile_connectivity(1)
    Right = Tile_connectivity(2)
    Down = Tile_connectivity(4)
    Left = Tile_connectivity(8)

class Tile_sheet_loder(object):
    def __init__(self,
                 tile_origins:Dict['str',Tuple[int,int]]):
        pass