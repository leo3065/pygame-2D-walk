import sys
import random
import enum

import pygame
import numpy as np

import map_gen
import tile
import img_util
from tile_type import Tile_type

pygame.init()
window_surface = pygame.display.set_mode((1200, 675))

pygame.display.set_caption('test draw')
window_surface.fill((0, 0, 0))

map_size = (48,24)
tile_size = 24
tile_path = 'asset/tile/mt_steel_1-5.png'

tile_loader = tile.Tile_sheet_loader(
    tile_path,
    tile_origin=(84, 163), tile_size=(24, 24), tile_unit=(25, 25), 
    transpert_key=(255, 0, 255),
    missing_key=(0, 128, 128),
    type_offsets={
        Tile_type.GROUND: (9 ,0),
        Tile_type.GROUND_ALT: (12 ,0),
        Tile_type.WALL: (0, 0),
        Tile_type.WALL_ALT: (3, 0),
        Tile_type.WALL_ALT_2: (6, 0),
        Tile_type.WATER: (18, 0),
        Tile_type.WATER_SPARKLE: (21,0),
    },
    connectiviy_offsets={
        tile.Tile_connectivity.from_dpad([2,3,6]): (0,0),
        tile.Tile_connectivity.from_dpad([1,2,3,4,6]): (1,0),
        tile.Tile_connectivity.from_dpad([1,2,4]): (2,0),
        tile.Tile_connectivity.from_dpad([2,3,6,8,9]): (0,1),
        tile.Tile_connectivity.from_dpad([1,2,3,4,6,7,8,9]): (1,1),
        tile.Tile_connectivity.from_dpad([1,2,4,7,8]): (2,1),
        tile.Tile_connectivity.from_dpad([6,8,9]): (0,2),
        tile.Tile_connectivity.from_dpad([4,6,7,8,9]): (1,2),
        tile.Tile_connectivity.from_dpad([4,7,8]): (2,2),

        tile.Tile_connectivity.from_dpad([2,6]): (0,3),
        tile.Tile_connectivity.from_dpad([4,6]): (1,3),
        tile.Tile_connectivity.from_dpad([2,4]): (2,3),
        tile.Tile_connectivity.from_dpad([2,8]): (0,4),
        tile.Tile_connectivity.from_dpad([]): (1,4),
        tile.Tile_connectivity.from_dpad([6,8]): (0,5),
        tile.Tile_connectivity.from_dpad([4,8]): (2,5),

        tile.Tile_connectivity.from_dpad([2]): (1,6),
        tile.Tile_connectivity.from_dpad([6]): (0,7),
        tile.Tile_connectivity.from_dpad([2,4,6,8]): (1,7),
        tile.Tile_connectivity.from_dpad([4]): (2,7),
        tile.Tile_connectivity.from_dpad([8]): (1,8),

        tile.Tile_connectivity.from_dpad([2,4,6]): (1,9),
        tile.Tile_connectivity.from_dpad([2,6,8]): (0,10),
        tile.Tile_connectivity.from_dpad([2,4,8]): (2,10),
        tile.Tile_connectivity.from_dpad([4,6,8]): (1,11),

        tile.Tile_connectivity.from_dpad([2,4,6,7,8,9]): (1,12),
        tile.Tile_connectivity.from_dpad([1,2,4,6,7,8]): (0,13),
        tile.Tile_connectivity.from_dpad([2,3,4,6,8,9]): (2,13),
        tile.Tile_connectivity.from_dpad([1,2,3,4,6,8]): (1,14),

        tile.Tile_connectivity.from_dpad([1,2,4,6,7,8,9]): (0,15),
        tile.Tile_connectivity.from_dpad([2,3,4,6,7,8,9]): (1,15),
        tile.Tile_connectivity.from_dpad([1,2,3,4,6,7,8]): (0,16),
        tile.Tile_connectivity.from_dpad([1,2,3,4,6,8,9]): (1,16),

        tile.Tile_connectivity.from_dpad([2,6,8,9]): (0,17),
        tile.Tile_connectivity.from_dpad([2,4,7,8]): (1,17),
        tile.Tile_connectivity.from_dpad([2,3,6,8]): (0,18),
        tile.Tile_connectivity.from_dpad([1,2,4,8]): (1,18),

        tile.Tile_connectivity.from_dpad([1,2,4,6]): (0,19),
        tile.Tile_connectivity.from_dpad([2,3,4,6]): (1,19),
        tile.Tile_connectivity.from_dpad([4,6,7,8]): (0,20),
        tile.Tile_connectivity.from_dpad([4,6,8,9]): (1,20),

        tile.Tile_connectivity.from_dpad([2,3,4,6,8]): (0,21),
        tile.Tile_connectivity.from_dpad([1,2,4,6,8]): (1,21),
        tile.Tile_connectivity.from_dpad([2,4,6,8,9]): (0,22),
        tile.Tile_connectivity.from_dpad([2,4,6,7,8]): (1,22),

        tile.Tile_connectivity.from_dpad([1,2,4,6,8,9]): (0,23),
        tile.Tile_connectivity.from_dpad([2,3,4,6,7,8]): (1,23),
    }
)

def map_draw(target_surface, map_tile_id, tile_loader,
             connected_tile_type=None, fallback_table=None):
    map_size = tuple(map_tile_id.shape)
    map_tile_id_padded = np.zeros((map_size[0]+2,map_size[1]+2)).astype(int)
    map_tile_id_padded[:,:] = 1
    map_tile_id_padded[1:-1,1:-1] = map_tile_id
    if connected_tile_type is None:
        connected_tile_type = {}
    if fallback_table is None:
        fallback_table = {}

    for y in range(map_size[1]):
        for x in range(map_size[0]):
            current_tile = map_tile_id[x,y]
            if current_tile in fallback_table:
                fallback_tile = fallback_table[current_tile]
            else:
                fallback_tile = None
            if map_tile_id[x,y] not in connected_tile_type:
                neighbors_array = (map_tile_id_padded[x:x+3,y:y+3] == map_tile_id[x,y]).T  # ij to xy
            else:
                neighbors_array = np.isin(map_tile_id_padded[x:x+3,y:y+3].T,  # ij to xy
                                          np.array([int(t) for t in connected_tile_type[current_tile]]))
            connectivity = tile.Tile_connectivity.from_neighbor_array(neighbors_array)

            img = tile_loader.tile_sprite(current_tile, connectivity, fallback_tile=fallback_tile)
            pygame_img = img_util.pil_image_to_surface(img)
            target_surface.blit(pygame_img, (x*tile_size, y*tile_size))

            if current_tile == Tile_type.WATER:
                img = tile_loader.tile_sprite(Tile_type.WATER_SPARKLE, connectivity)
                pygame_img = img_util.pil_image_to_surface(img)
                target_surface.blit(pygame_img, (x*tile_size, y*tile_size))

map_surface = pygame.Surface((map_size[0]*tile_size, map_size[1]*tile_size))

tile_replace_table = [
    (
        Tile_type.GROUND,  
        {Tile_type.GROUND, Tile_type.WATER, Tile_type.GROUND_ALT},
        {c for c in tile.Tile_connectivity.all_connectivity() if int(c) not in [0xFF, 0x9F, 0x3F, 0x8F, 0xAF]},
        {
            Tile_type.GROUND: 2,
            Tile_type.GROUND_ALT: 1,
        }),
    (
        Tile_type.GROUND,  
        {Tile_type.GROUND, Tile_type.WATER, Tile_type.GROUND_ALT},
        {tile.Tile_connectivity.FULL},
        {
            Tile_type.GROUND: 4,
            Tile_type.GROUND_ALT: 1,
        }),
    (
        Tile_type.WALL,  
        None,
        {tile.Tile_connectivity.FULL},
        {
            Tile_type.WALL: 4,
            Tile_type.WALL_ALT: 1,
            Tile_type.WALL_ALT_2: 1,
        }),
]
tile_connect_table = {
    Tile_type.GROUND_ALT: {Tile_type.GROUND, Tile_type.GROUND_ALT, Tile_type.WATER},
    Tile_type.WALL: {Tile_type.WALL, Tile_type.WALL_ALT, Tile_type.WALL_ALT_2},
    Tile_type.WALL_ALT: {Tile_type.WALL, Tile_type.WALL_ALT, Tile_type.WALL_ALT_2},
    Tile_type.WALL_ALT_2: {Tile_type.WALL, Tile_type.WALL_ALT, Tile_type.WALL_ALT_2},
}
tile_fallback_table = {
    Tile_type.GROUND_ALT: Tile_type.GROUND,
}

def map_init():
    map_tile_id = map_gen.base_map_gen(map_size)
    map_tile_id = map_gen.map_replace_tile_ids(map_tile_id, tile_replace_table)

    map_draw(map_surface, map_tile_id, tile_loader, tile_connect_table, tile_fallback_table)
    window_surface.blit(map_surface, (0,0))

map_init()
pygame.display.update()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                map_init()
                pygame.display.update()