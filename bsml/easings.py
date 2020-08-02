
import math

# https://easings.net/

# magic numbers used by the "back" easings
c1 = 1.70158
c2 = c1 * 1.525

easings = {
    "linear":     lambda x: x,
    "inSine":     lambda x: 1 - math.cos((x * math.pi) / 2),
    "outSine":    lambda x: math.sin((x * math.pi) / 2),
    "inOutSine":  lambda x: -(math.cos(math.pi * x) - 1) / 2,
    "inCubic":    lambda x: pow(x, 3),
    "outCubic":   lambda x: 1 - pow(1 - x, 3),
    "inOutCubic": lambda x: 4 * pow(x, 3) if x < 0.5 else 1 - math.pow(-2 * x + 2, 3) / 2,
    "inBack":     lambda x: (c1 + 1) * pow(x, 3) - c1 * pow(x, 2),
    "outBack":    lambda x: 1 + (c1 + 1) * pow(x - 1, 3) + c1 * pow(x - 1, 2),
    "inOutBack":  lambda x: (pow(2 * x, 2) * ((c2 + 1) * 2 * x - c2)) / 2 if x < 0.5 else (pow(2 * x - 2, 2) * ((c2 + 1) * (x * 2 - 2) + c2) + 2) / 2,
    "semicircle": lambda x: math.sqrt(1 - pow(2*x - 1, 2)) 
}

def ez(easing, x=1):
    #print("getting easing for %s" % x)
    if easing in easings:
        return easings[easing](x)
    else:
        ret = eval(easing)
        return ret
