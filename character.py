import pygame
from pygame.math import Vector2, Vector3

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

        self.position_offset = Vector3(0,0,0)
        self.state = 'idle'
        self.sprite_type = 'stand'

        self.frame_until_next_event = 0
        self.animation_queue = []
        
    def collision_rect(self):
        return self.rect_collision_base.move(self.position)
    
    def try_move(self, offset: Tuple[int,int]=None) -> (Vector2, pygame.Rect):
        if offset is None:
            offset = self.speed
        offset = Vector2(offset)
        new_pos = self.position + offset
        return (new_pos, self.rect_collision_base.move(new_pos))
    
    def move(self):
        self.position += Vector2(self.speed)
    
    def animate(self, **kwargs):
        if self.state == 'idle' and self.speed.length() > 0:
            self.state = 'flying'
            self.animation_queue = [
                [3, {'set_sprite': 'pmove_0', 'set_position_offset': (0,0,1)}],
                [3, {'set_sprite': 'pmove_1', 'set_position_offset': (0,0,1)}],
                [3, {'set_sprite': 'pmove_0', 'set_position_offset': (0,0,0)}],
                [3, {'set_sprite': 'pmove_1', 'set_position_offset': (0,0,0)}],
                [3, {'set_sprite': 'flying', 'set_position_offset': (0,0,0)}],
            ]
            self.frame_until_next_event = 0
        elif self.state == 'flying' and self.speed.length() == 0 and kwargs['current_tile_type']!='water':
            self.state = 'idle'
            self.animation_queue = [
                [3, {'set_sprite': 'pmove_1', 'set_position_offset': (0,0,1)}],
                [3, {'set_sprite': 'pmove_0', 'set_position_offset': (0,0,1)}],
                [3, {'set_sprite': 'pmove_1', 'set_position_offset': (0,0,0)}],
                [3, {'set_sprite': 'pmove_0', 'set_position_offset': (0,0,0)}],
                [3, {'set_sprite': 'stand', 'set_position_offset': (0,0,0)}],
            ]
            self.frame_until_next_event = 0

        animation_queue = self.animation_queue
        if animation_queue == []:
            if self.state == 'idle':
                animation_queue.extend(
                    [
                        [60, {'set_sprite': 'stand', 'set_position_offset': (0,0,0)}],
                        [2, {'set_sprite': 'pmove_0', 'set_position_offset': (0,0,2)}],
                        [3, {'set_sprite': 'pmove_0', 'set_position_offset': (0,0,3)}],
                        [2, {'set_sprite': 'pmove_0', 'set_position_offset': (0,0,2)}],
                    ])
            elif self.state == 'flying':
                animation_queue.extend(
                    [
                        [20, {'set_position_offset': (0,0,0)}],
                        [20, {'set_position_offset': (0,0,1)}],
                        [20, {'set_position_offset': (0,0,0)}],
                        [20, {'set_position_offset': (0,0,-1)}],
                    ])
        

        if self.frame_until_next_event <= 0:
            frame_duration, events = animation_queue.pop(0)
            if 'set_position_offset' in events:
                self.position_offset = Vector3(events['set_position_offset'])
            if 'set_sprite' in events:
                self.sprite_type = events['set_sprite']
            self.frame_until_next_event = frame_duration
        self.frame_until_next_event -= 1

    def draw(self, surface: pygame.Surface):
        shadow_surface = pygame.Surface(self.rect_collision_base.size, pygame.SRCALPHA)
        shadow_surface.fill((255,255,255,0))
        pygame.draw.ellipse(shadow_surface, (0,0,0,128), pygame.Rect((0,0), self.rect_collision_base.size))
        surface.blit(shadow_surface, self.position + self.rect_collision_base.topleft)

        img = self.sprite_loader.get_sprite_img(self.sprite_type, self.facing)
        sprite_surface = img_util.pil_image_to_surface(img)
        display_offset = Vector2(self.position_offset.x,
                                 self.position_offset.y - self.position_offset.z)
        surface.blit(sprite_surface, self.position-self.sprite_origin+display_offset)
    
