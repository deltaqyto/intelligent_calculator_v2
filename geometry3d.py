from baseitem import BaseItem
from math import pi


class Shape3d(BaseItem):
    def __init__(self):
        super().__init__()
        self.vars = ["x", "y", "z", "volume", "area"]


class Sphere(Shape3d):
    def __init__(self, **kwargs):
        super().__init__()
        self.vars += ["r", "diameter"]
        self.equations = {frozenset(["r", "x"]): lambda i: i["r"] - i["x"],
                          frozenset(["r", "y"]): lambda i: i["r"] - i["y"],
                          frozenset(["r", "z"]): lambda i: i["r"] - i["z"],
                          frozenset(["r", "volume"]): lambda i: i["r"] ** 3 * pi * 4/3 - i["volume"],
                          frozenset(["r", "area"]): lambda i: i["r"] ** 2 * pi * 4 - i["area"],
                          frozenset(["r", "diameter"]): lambda i: i["r"] * 2 - i["diameter"]}
        self.finish_init(**kwargs)
        