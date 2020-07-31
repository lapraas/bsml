
import math

class Wall:
    def __init__(self, beat, dur, l, r, d, u, rot=0, lrotx=0, lroty=0, lrotz=0):
        self.beat = beat
        self.dur = dur
        self.l = l
        self.r = r
        self.d = d
        self.u = u
        self.rot = rot
        self.lrotx = lrotx
        self.lroty = lroty
        self.lrotz = lrotz
        #print("new wall created (%s, %s, %s, %s)" % (self.l, self.r, self.d, self.u))
        if self.r < self.l:
            raise Exception("Wall with bad dimensions (r: %s, l: %s" % (self.r, self.l))
        if self.u < self.d:
            raise Exception("Wall with bad dimensions (u: %s, d: %s" % (self.u, self.d))
    
    def __str__(self):
        return str(self.__dict__)
    
    def getWidth(self):
        return self.r - self.l
    
    def getHeight(self):
        return self.u - self.d
    
    def mirror(self):
        """ Returns a new Wall mirrored over the middle of the lanes."""
        return Wall(self.beat, self.dur, -self.r, -self.l, self.d, self.u, -self.rot, self.lrotx, -self.lroty, -self.lrotz)
    
    def clone(self, beat):
        """ Returns an identical Wall at the given beat. """
        return Wall(beat, self.dur, self.l, self.r, self.d, self.u)
    
    def json(self):
        """ Get the wall as a json object. """
        beat = self.beat + 1.4 # replace with hjd
        w, h = self.getWidth(), self.getHeight()
        
        return {
            "_time": beat,
            "_duration": self.dur,
            "_lineIndex": 0,
            "_type": 0,
            "_width": 0,
            "_customData": {
                # to undo the local rotation z transform we have to take trig parts of it and multiply them by the dimensions of the wall, then add them to the position
                "_position": [self.l + math.cos(math.radians(self.lrotz - 90)) * h / 2, self.d + math.sin(math.radians(self.lrotz-90)) * h / 2 + h / 2],
                #"_position": [self.l, self.d],
                "_scale": [w, h],
                "_rotation": self.rot,
                "_localRotation": [self.lrotx, self.lroty, self.lrotz]
            }
        }
