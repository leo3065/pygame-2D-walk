import sys
import random

import pygame
import numpy as np

import map_gen

pygame.init()
window_surface = pygame.display.set_mode((800, 600))

pygame.display.set_caption('test draw')
window_surface.fill((0, 0, 0))

map_size = (30,20)
tile_size = 24

map_tile_id = map_gen.base_map_gen(map_size)
tile_colors = {
    0: (0, 255, 0),
    1: (255, 0, 0),
    2: (0, 0, 255),
    }

base_rect = pygame.Rect(1, 1, 23, 23)
for y in range(map_size[1]):
    for x in range(map_size[0]):
        draw_rect = base_rect.move(x*tile_size, y*tile_size)
        color = pygame.Color(tile_colors[map_tile_id[x,y]])
        pygame.draw.rect(window_surface, color, draw_rect)

pygame.display.update()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()