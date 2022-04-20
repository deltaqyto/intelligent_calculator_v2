from random import random
import math
import igraph as ig


class BaseItem:
    def __init__(self):
        self.vars = []
        self.equations = {}
        self.matched = {}

    def finish_init(self, **kwargs):
        self.matched = {k: kwargs[k] for k in self.vars if k in kwargs}

        self.solve_graph = ig.Graph()
        self.solve_graph.add_vertices(len(self.vars))
        self.edge_table = []
        for identity, equation in self.equations.items():


        print(f"Created {self}")

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join([f'{q}: {v}' for q, v in self.matched.items()])})"

    def solve(self, target):
        known = frozenset([k for k in self.matched] + [target])
        print(known)

        return
        for identity, equation in self.equations.items():
            if not identity[1].issubset(known):
                continue
            return self.iterative_solve(identity, equation, target)

        print(f"Unable to match {target, known}")

    def iterative_solve(self, i, e, t):
        if i[0] == t:
            return e(self.matched)
        q = -1
        fx = None
        dx = None
        # newton solve
        guess = random()
        temp_known = self.matched.copy()
        for q in range(100):
            temp_known[t] = guess
            fx = e(temp_known) - self.matched[i[0]]
            # if abs(fx) <= 1e-10:
            #    break

            temp_known[t] = guess + 0.001
            dx = e(temp_known)

            temp_known[t] = guess - 0.001
            dx = (dx - e(temp_known)) / 0.002
            guess -= fx/dx
            if not q % 50:
                print(f"Iter {q}: x={guess}, f={fx}, d={dx}")
        print(f"Iter {q}: x={guess}, f={fx}, d={dx}")
        return guess

    def __getattr__(self, item):
        if item not in self.vars:
            raise AttributeError(f"{self.__class__.__name__} does not recognise {item}")
        if item in self.matched:
            return self.matched[item]
        return self.solve(item)


class Vector(BaseItem):
    def __init__(self, **kwargs):
        super().__init__()
        self.vars = ["x", "y", "mag", "angle"]
        self.equations = {("mag", frozenset(["x", "y", "mag"])): lambda i: (i["x"] ** 2 + i["y"] ** 2) ** 0.5,
                          ("mag", frozenset(["x", "angle", "mag"])): lambda i: (i["x"] / math.cos(math.radians(i["angle"]))),
                          ("mag", frozenset(["y", "angle", "mag"])): lambda i: (i["y"] / math.sin(math.radians(i["angle"])))}

        self.finish_init(**kwargs)


def main():
    c = Vector(angle=45, y=1).x
    print(c)


if __name__ == "__main__":
    main()
