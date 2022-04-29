import math

from baseitem import BaseItem


class Test(BaseItem):
    def __init__(self):
        self.passed = True
        kwargs = {"a": 1}
        super().__init__()
        self.vars = ["a", "b", "c", ""]
        self.equations = {frozenset(["a", "b"]): lambda i: i['a'] + 1 - i["b"],
                          frozenset(["b", "c"]): lambda i: i['c'] / 2 - i["b"]}

        self.finish_init(**kwargs)
        self.test(self.solve("c"), 4)

        kwargs = {"r": 2 ** 0.5, "a": 45}
        self.vars = ["r", "a", "x", "y"]
        self.equations = {frozenset(["r", "x", "y"]): lambda i: (i["x"] ** 2 + i["y"] ** 2) ** 0.5 - i["r"],
                          frozenset(["a", "x", "y"]): lambda i: (math.degrees(math.atan2(i["y"], i["x"])) - i["a"])}

        self.finish_init(**kwargs)
        self.test(self.solve("x"), 1)
        self.test(self.solve("y"), 1)

        kwargs = {"g": 1}
        self.vars = ["r", "g"]
        self.equations = {frozenset(["r", "g"]): lambda i: (-i["g"] - i["r"])}

        self.finish_init(**kwargs)
        self.test(self.solve("r"), -1)

        if self.passed:
            print("-" * 20)
            print("Passed all tests")
            print("-" * 20)
        else:
            print("-"*20)
            print("Failed tests")
            exit()

    def test(self, e, v):
        try:
            assert e == v
        except Exception as exc:
            print(f"Failed test {e} == {v}", exc)
            self.passed = False

