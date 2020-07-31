
from Structure import Structure
from Wall import Wall
from easings import ez

def create(beat, dur, l, r, d, u, rot=[0], lrotx=[0], lroty=[0], lrotz=[0], length=None, step=None, mirror=[0]):
    if length == None: length = [*dur]
    if step == None: step = [*dur]
    walls = []
    if step[0] < dur[0]:
        curBeat = 0
        delta = lambda arg: ez("linear" if not len(arg) > 2 else arg[2], prog) * ((arg[0] if not len(arg) > 1 else arg[1]) - arg[0])
        while curBeat < dur[0]:
            prog = curBeat / dur[0]
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
            newWall = Wall(beat + curBeat, length[0] + dleng, l[0] + dl, r[0] + dr, d[0] + dd, u[0] + du, rot[0] + drot, lrotx[0] + dlrotx, lroty[0] + dlroty, lrotz[0] + dlrotz)
            walls.append(newWall)
            
            curBeat += (step[0] + dstep)
    else:
        newWall = Wall(beat, length[0], l[0], r[0], d[0], u[0], rot[0], lrotx[0], lroty[0], lrotz[0])
        walls.append(newWall)
    
    structure = Structure(walls)
    if mirror[0]: structure.mirror()
    return structure
