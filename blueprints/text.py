
from bsml.Wall import Wall
from bsml.nyri0 import load_font, getTextWidth

font = load_font()

def create(beat, text, x, y, spacing, sx, sy, rotx=0, roty=0, rotz=0, lrotx=0, lroty=0, lrotz=0, njs=None, njo=None, anim=None, **kwargs):
    walls = []
    
    offset = 0
    scale = 0.1
    
    totalTextWidth = getTextWidth(text, font) * scale + spacing * len(text)
        
    for i, char in enumerate(text):
        if not char in font:
            raise Exception("Character '%s' is not a part of the supported alphabet" % char)
        for wall in font[char][1]:
            print("%s: %s" % (i, wall))
            posx = scale * sx * wall[0] + offset - totalTextWidth/2
            posy = scale * sy * wall[1]
            charWall = Wall(beat, 0.02, posx, posx + scale * sx * wall[2], posy, posy + scale * sy * wall[3])
            walls.append(charWall)
        offset += scale * sx * font[char][0] + spacing
    
    return walls
