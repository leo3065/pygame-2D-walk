import pygame
import numpy as np

import tile
import img_util

class Game_map(object):
    def __init__(self, tile_id_np, tile_name_table,
                 tile_loader):
        self.size = tile_id_np.shape
        self.tile_id_np = tile_id_np
        
        self.tile_loader = tile_loader
        tile_size = tile_loader.tile_size
        self.size_pixel = (self.size[0]*tile_size[0], self.size[1]*tile_size[1])
        self.surface = pygame.Surface(self.size_pixel)

        self.tile_name_table = tile_name_table
        self.tile_id_table = {name: id for id, name in tile_name_table.items()}

        animated_tile_type_ids = [self.tile_id_table[name]
                                  for name in self.tile_loader.animated_tile_types]
        animated_tiles = []
        map_size = self.size
        map_tile_id_np = self.tile_id_np
        for y in range(map_size[1]):
            for x in range(map_size[0]):
                current_tile = map_tile_id_np[x,y]
                if current_tile in animated_tile_type_ids:
                    animated_tiles.append((x,y))
        self.animated_tiles = animated_tiles
        
        self.update_suface()

    def update_suface(self):
        map_size = self.size
        map_tile_id_np = self.tile_id_np
        map_tile_id_padded = np.zeros((map_size[0]+2,map_size[1]+2)).astype(int)
        map_tile_id_padded[:,:] = 1
        map_tile_id_padded[1:-1,1:-1] = map_tile_id_np

        tile_loader = self.tile_loader
        tile_size = tile_loader.tile_size
        for y in range(map_size[1]):
            for x in range(map_size[0]):
                current_tile = map_tile_id_np[x,y]
                neighbors_array = (map_tile_id_padded[x:x+3,y:y+3] == map_tile_id_np[x,y]).T  # ij to xy
                connectivity = tile.Tile_connectivity.from_neighbor_array(neighbors_array)

                current_tile_name = self.tile_name_table[current_tile]
                img = self.tile_loader.get_tile_img(current_tile_name, connectivity)
                pygame_img = img_util.pil_image_to_surface(img)
                self.surface.blit(pygame_img, (x*tile_size[0], y*tile_size[1]))

                if current_tile_name == 'water':
                    img = tile_loader.get_tile_img('water_sparkle', connectivity)
                    pygame_img = img_util.pil_image_to_surface(img)
                    self.surface.blit(pygame_img, (x*tile_size[0], y*tile_size[1]))
    
    def get_tile_id_at(self, coord, use_pixels=False):
        xx, yy = coord
        if use_pixels:
            tile_size = self.tile_loader.tile_size
            xx /= tile_size[0]
            yy /= tile_size[1]
        return self.tile_id_np[int(xx), int(yy)]
    
    def get_tile_name_at(self, coord, use_pixels=False):
        return self.tile_name_table[self.get_tile_id_at(coord, use_pixels)]
    
    def tile_coord_to_pixel_coord(self, tile_coord, tile_offset=(0,0)):
        tile_size = self.tile_loader.tile_size
        return (tile_coord[0]*tile_size[0]+tile_offset[0], tile_coord[1]*tile_size[1]+tile_offset[1])