from baseitem import BaseItem
from math import pi


class Shape2d(BaseItem):
    def __init__(self):
        super().__init__()
        self.vars = ["x", "y", "area", "perimeter"]


class Circle(Shape2d):
    def __init__(self, **kwargs):
        super().__init__()
        self.vars += ["r", "diameter"]
        self.equations = {frozenset(["r", "area"]): lambda i: i["r"] ** 2 * pi - i["area"],
                          frozenset(["r", "perimeter"]): lambda i: i["r"] * 2 * pi - i["perimeter"],
                          frozenset(["r", "x"]): lambda i: i["r"] - i["x"],
                          frozenset(["r", "y"]): lambda i: i["r"] - i["y"],
                          frozenset(["r", "diameter"]): lambda i: i["r"] * 2 - i["diameter"]}

        self.finish_init(**kwargs)
        