import pygame
from pygame.math import Vector2

from sprite import  Facing, Sprite_sheet_loader
import img_util

from typing import *


class Character(object):
    def __init__(self,
                 rect_collision_base: pygame.Rect,
                 sprite_loader: Sprite_sheet_loader,
                 sprite_origin: Tuple[int,int]):
        self.position = Vector2(0, 0)
        self.speed = Vector2(0, 0)
        self.facing = Facing.DOWN
        self.rect_collision_base = rect_collision_base
        self.sprite_loader = sprite_loader
        self.sprite_origin = Vector2(sprite_origin)
    
    def try_move(self, offset: Tuple[int,int]=None) -> (Vector2, pygame.Rect):
        if offset is None:
            offset = self.speed
        offset = Vector2(offset)
        new_pos = self.position + offset
        return (new_pos, self.rect_collision_base.move(new_pos))
    
    def move(self, offset: Tuple[int,int]=None):
        if offset is None:
            offset = self.speed
        self.position += Vector2(offset)
    
    def collision_rect(self):
        return self.rect_collision_base.move(self.position)

    def draw(self, surface: pygame.Surface):
        shadow_surface = pygame.Surface(self.rect_collision_base.size, pygame.SRCALPHA)
        shadow_surface.fill((255,255,255,0))
        pygame.draw.ellipse(shadow_surface, (0,0,0,128), pygame.Rect((0,0), self.rect_collision_base.size))
        surface.blit(shadow_surface, self.position + self.rect_collision_base.topleft)

        img = self.sprite_loader.get_sprite_img('move', self.facing)
        sprite_surface = img_util.pil_image_to_surface(img)
        surface.blit(sprite_surface, self.position-self.sprite_origin)
    
