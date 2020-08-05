
from bsml.Wall import Wall
from bsml.nyri0 import load_font

font = load_font()

def create(beat, len, text, x, y, centering, sx, sy, rotx=0, roty=0, rotz=0, lrotx=0, lroty=0, lrotz=0, njs=None, njo=None, **kwargs):
    
    for char in text:
        for wall in font[char]:
            posx = sx * wall[0]
            posy = sy * wall[1]
    
    wall = Wall
    return wall
