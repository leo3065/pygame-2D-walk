import sys
import random
import enum

missing_module = []
try:
    import pygame
except ModuleNotFoundError:
    missing_module.append('pygame')
try:
    import numpy
except ModuleNotFoundError:
    missing_module.append('numpy')
try:
    import scipy
except ModuleNotFoundError:
    missing_module.append('scipy')
try:
    import PIL
except ModuleNotFoundError:
    missing_module.append('Pillow')
if missing_module:
    print('The following module is required')
    print(f'- {", ".join(missing_module)}')
    print('Please run the following in command prompt to install:')
    print(f'pip install -U {" ".join(missing_module)}')
    input('Press Enter to continue...')
    sys.exit()


import pygame
from  pygame.math import Vector2
import numpy as np

from game_map import Game_map
import map_gen
import tile
from character import Facing, Character
from sprite import Sprite_sheet_loader
import img_util

map_size = (48,24)
tile_path = 'asset/tile/mt_steel_1-5.png'

tile_loader = tile.Tile_sheet_loader(
    tile_path,
    tile_origin=(84, 163), tile_size=(24, 24), tile_unit=(25, 25), 
    transpert_key=(255, 0, 255),
    missing_key=(0, 128, 128),
    type_offsets={
        ('ground', 0): (9 ,0),
        ('ground', 1): (12 ,0),
        ('wall',0): (0, 0),
        ('wall',1): (3, 0),
        ('wall',2): (6, 0),
        ('water',0): (18, 0),
        ('water_sparkle',0): (21,0),
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
tile_name_table = {
    0: 'ground',
    1: 'wall',
    2: 'water',
}

map_tile_id = map_gen.base_map_gen_hill(map_size)
game_map = Game_map(map_tile_id, tile_name_table, tile_loader)


sprite_path = 'asset/character/skarmory.png'
player_sprite_sheet_loader = Sprite_sheet_loader(
    path=sprite_path,
    sprite_origin=(41,1), sprite_size=(41,35), sprite_unit=(42,36),
    type_offsets={
        'stand': (0,0),
        'pmove_0': (0,1),
        'pmove_1': (0,2),
        'flying': (0,3),
    },
    facing_offsets={
        Facing.DOWN: (0,0),
        Facing.DOWN_LEFT: (1,0),
        Facing.LEFT: (2,0),
        Facing.UP_LEFT: (3,0),
        Facing.UP: (4,0),
    },
    transpert_key=(0,128,128),
    )

player = Character(
    rect_collision_base=pygame.Rect((-10,-5),(20,10)),
    sprite_loader=player_sprite_sheet_loader,
    sprite_origin=(20,30),
    )
player.position = Vector2(0)
while True:
    spawn_pos = (random.randint(0, map_size[0]-1), random.randint(0, map_size[1]-1))
    new_pos, new_rect = player.try_move(game_map.tile_coord_to_pixel_coord(spawn_pos))
    if all(game_map.get_tile_name_at(c, use_pixels=True) != 'wall'
           for c in [new_rect.topleft, new_rect.topright, new_rect.bottomleft, new_rect.bottomright]):
        break
spawn_pos = game_map.tile_coord_to_pixel_coord(spawn_pos, tile_offset=(0.5,0.5))
player.position = Vector2(spawn_pos)


map_size_pixel = tuple(int(p) for p in game_map.tile_coord_to_pixel_coord(map_size))
display_area_size = (360,270)
scale_ratio = 2
display_area_rect = pygame.Rect((0,0), display_area_size)

actual_window_size = (display_area_size[0]*scale_ratio, display_area_size[1]*scale_ratio)
pygame.init()
window_surface = pygame.display.set_mode(actual_window_size)

pygame.display.set_caption('test charater')
window_surface.fill((0, 0, 0))

clock = pygame.time.Clock()
finished = False
buffer_suface = pygame.Surface(game_map.surface.get_size())
display_area_suface = pygame.Surface(display_area_rect.size)

while not finished:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                map_tile_id = map_gen.base_map_gen_hill(map_size)
                game_map = Game_map(map_tile_id, tile_name_table, tile_loader)
                
                player.position = Vector2(0)
                while True:
                    spawn_pos = (random.randint(0, map_size[0]-1), random.randint(0, map_size[1]-1))
                    new_pos, new_rect = player.try_move(game_map.tile_coord_to_pixel_coord(spawn_pos))
                    if all(game_map.get_tile_name_at(c, use_pixels=True) != 'wall'
                        for c in [new_rect.topleft, new_rect.topright, new_rect.bottomleft, new_rect.bottomright]):
                        break
                spawn_pos = game_map.tile_coord_to_pixel_coord(spawn_pos, tile_offset=(0.5,0.5))
                player.position = Vector2(spawn_pos)


    key_is_pressed = pygame.key.get_pressed()
    player.speed.x = (key_is_pressed[pygame.K_RIGHT]-key_is_pressed[pygame.K_LEFT])
    player.speed.y = (key_is_pressed[pygame.K_DOWN]-key_is_pressed[pygame.K_UP])

    if player.speed.length() > 0:
        player.speed.scale_to_length(2)
        player.facing = Facing.from_vector(player.speed)
    
    new_pos, new_rect = player.try_move()
    if all(game_map.get_tile_name_at(c, use_pixels=True) != 'wall'
           for c in [new_rect.topleft, new_rect.topright, new_rect.bottomleft, new_rect.bottomright]):
        player.move()
    player.animate()
    

    display_area_rect.center = player.position
    display_area_rect.left = max(display_area_rect.left, 0)
    display_area_rect.top = max(display_area_rect.top, 0)
    display_area_rect.right = min(display_area_rect.right, map_size_pixel[0])
    display_area_rect.bottom = min(display_area_rect.bottom, map_size_pixel[1])

    buffer_suface.blit(game_map.surface, (0,0))
    player.draw(buffer_suface)
    
    display_area_suface.blit(buffer_suface, (0,0), display_area_rect)
    pygame.transform.scale(display_area_suface, actual_window_size, window_surface)
    pygame.display.update()

    clock.tick(60)

pygame.quit()
sys.exit()