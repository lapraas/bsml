
from bsml.Wall import Wall

def create(beat, dur, l, r, d, u, rotx=0, roty=0, rotz=0, lrotx=0, lroty=0, lrotz=0, njs=None, njo=None, anim=None, **kwargs):
    newWall = Wall(beat, dur, l, r, d, u, [rotx, roty, rotz], [lrotx, lroty, lrotz])
    return newWall
