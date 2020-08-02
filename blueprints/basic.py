
from bsml.Wall import Wall

def create(beat, len, l, r, d, u, rot=0, lrotx=0, lroty=0, lrotz=0, *args):
    newWall = Wall(beat, len, l, r, d, u, rot, lrotx, lroty, lrotz)
    return newWall
