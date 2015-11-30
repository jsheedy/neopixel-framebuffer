
def accxyz(addr, *args, axis=1,point=None):
    """self, addr, x, y, z"""

    pos = (args[axis] + 1) / 2
    point.set(pos)

