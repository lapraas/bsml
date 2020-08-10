
from bsml.Wall import Wall
from math import cos, sin, radians

def create(beat, dur, rx, ry, phase, l, r, d, u, cx=0, cy=0, rotx=0, roty=0, rotz=0, lrotx=0, lroty=0, lrotz=0, njs=None, njo=None, anim=None, **kwargs):
    x = (rx) * cos(radians(phase)) + (cx) 
    y = (ry) * sin(radians(phase)) + (cy)
    
    wall = Wall(beat, dur, x + l, x + r, y + d, y + u, [rotx, roty, rotz], [lrotx, lroty, lrotz])
    return wall
