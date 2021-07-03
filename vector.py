import dataclasses
import math
import numbers

from  typing import *


@dataclasses.dataclass
class Vector2D(object):
    x: float
    y: float

    def __neg__(self):
        return Vector2D(-self.x, -self.y)
    
    def __abs__(self):
        return Vector2D(abs(self.x), abs(self.y))

    def __round__(self):
        return Vector2D(round(self.x), round(self.y))
        
    def __floor__(self):
        return Vector2D(math.floor(self.x), math.floor(self.y))

    def __ceil__(self):
        return Vector2D(math.ceil(self.x), math.ceil(self.y))

    def __trunc__(self):
        return Vector2D(math.trunc(self.x), math.trunc(self.y))

    def __add__(self, other):
        if isinstance(other, numbers.Number):
            other = Vector2D(other, other)
        if not isinstance(other, Vector2D):
            other = Vector2D(other)
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        if isinstance(other, numbers.Number):
            other = Vector2D(other, other)
        if not isinstance(other, Vector2D):
            other = Vector2D(other)
        return Vector2D(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            other = Vector2D(other, other)
        if not isinstance(other, Vector2D):
            other = Vector2D(other)
        return Vector2D(self.x * other.x, self.y * other.y)
        
    def __truediv__(self, other):
        if isinstance(other, numbers.Number):
            other = Vector2D(other, other)
        if not isinstance(other, Vector2D):
            other = Vector2D(other)
        return Vector2D(self.x / other.x, self.y / other.y)
        
    def __floordiv__(self, other):
        if isinstance(other, numbers.Number):
            other = Vector2D(other, other)
        if not isinstance(other, Vector2D):
            other = Vector2D(other)
        return Vector2D(self.x // other.x, self.y // other.y)
        
    def __mod__(self, other):
        if isinstance(other, numbers.Number):
            other = Vector2D(other, other)
        if not isinstance(other, Vector2D):
            other = Vector2D(other)
        return Vector2D(self.x % other.x, self.y % other.y)

    def __eq__(self, other):
        if not isinstance(other, Vector2D):
            other = Vector2D(other)
        return self.x == other.x and self.y == other.y
    
    def length(self):
        x, y = self.x, self.y
        return (x**2 + y**2)**.5
    
    def __str__(self):
        return f'{self.x}, {self.y}'
