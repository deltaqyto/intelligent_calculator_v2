import math

from tests import Test
from baseitem import BaseItem
from geometry2d import *
from geometry3d import *


class Vector(BaseItem):
    def __init__(self, **kwargs):
        super().__init__()
        self.vars = ["x", "y", "mag", "angle"]
        self.equations = {frozenset(["x", "y", "mag"]): lambda i: (i["x"] ** 2 + i["y"] ** 2) ** 0.5 - i["mag"],
                          frozenset(["x", "angle", "mag"]): lambda i: (i["x"] / math.cos(math.radians(i["angle"]))) - i["mag"],
                          frozenset(["y", "angle", "mag"]): lambda i: (i["y"] / math.sin(math.radians(i["angle"]))) - i["mag"]}

        self.finish_init(**kwargs)


class Multivector(BaseItem):
    def __init__(self, **kwargs):
        print(kwargs)
        super().__init__()
        self.vars = ["res", "v"]
        self.equations = {frozenset(["res", "v"]): (lambda i: Vector(x=i["x"], y=i["y"], silent=True), ("x", "y"),
                                                    (lambda t, i: t.x - sum([v.x for v in i["v"]]),
                                                     lambda t, i: t.y - sum([v.y for v in i["v"]])))}
        self.finish_init(**kwargs)


def main():
    c = Vector(angle=45, y=1, silent=True).x
    print(c)
    c = Multivector(v=[Vector(x=1, y=2), Vector(x=-1, y=-1)]).res
    print(c)

    print(Sphere(r=5).shadow)


if __name__ == "__main__":
    Test()
    main()



"""
eq 1: x, y = angle
eq 2: x, y = mag

from angle, mag -> x, y
"""