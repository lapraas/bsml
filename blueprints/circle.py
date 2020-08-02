
from bsml.Wall import Wall
from math import cos, sin, radians

def create(beat, len, rx, ry, phase, l, r, d, u, cx=0, cy=0, rot=0, lrotx=0, lroty=0, lrotz=0, **kwargs):
    x = (rx) * cos(radians(phase)) + (cx) 
    y = (ry) * sin(radians(phase)) + (cy)
    
    wall = Wall(beat, len, x + l, x + r, y + d, y + u, rot, lrotx, lroty, lrotz)
    return wall
