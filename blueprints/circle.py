
from Structure import Structure
from Wall import Wall
from easings import ez

import math

def create(beat, dur, rx, ry, phase, l, r, d, u, cx=[0], cy=[0], rot=[0], lrotx=[0], lroty=[0], lrotz=[0], length=None, step=None, mirror=False):
    if length == None: length = [*dur]
    if step == None: step = [*dur]
    
    walls = []
    
    if step[0] < dur[0]:
        cBeat = 0
        delta = lambda arg: ez("linear" if not len(arg) > 2 else arg[2], prog) * ((arg[0] if not len(arg) > 1 else arg[1]) - arg[0])
        while cBeat < dur[0]:
            prog = cBeat / dur[0]
            drx = delta(rx)
            dry = delta(ry)
            dcx = delta(cx)
            dcy = delta(cy)
            dphase = delta(phase)
            dl = delta(l)
            dr = delta(r)
            dd = delta(d)
            du = delta(u)
            drot = delta(rot)
            dlrotx = delta(lrotx)
            dlroty = delta(lroty)
            dlrotz = delta(lrotz)
            dleng = delta(length)
            dstep = delta(step)
            
            #print(dphase)
            
            x = (rx[0] + drx) * math.cos(math.radians(phase[0] + dphase)) + (cx[0] + dcx) 
            y = (ry[0] + dry) * math.sin(math.radians(phase[0] + dphase)) + (cy[0] + dcy)
            #print(x, y)
            
            wall = Wall(beat + cBeat,
                length[0] + dleng,
                x + l[0] + dl,
                x + r[0] + dr,
                y + d[0] + dd,
                y + u[0] + du,
                rot[0] + drot,
                lrotx[0] + dlrotx,
                lroty[0] + dlroty,
                lrotz[0] + dlrotz)
            walls.append(wall)
            
            cBeat += (step[0] + dstep)
    
    structure = Structure(walls)
    if int(mirror): structure.mirror()
    return structure
            