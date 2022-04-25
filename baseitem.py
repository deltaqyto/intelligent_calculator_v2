import igraph as ig
import numpy as np
from random import random


class BaseItem:
    def __init__(self):
        self.vars = []
        self.equations = {}
        self.matched = {}
        self.solve_graph = ig.Graph()

    def finish_init(self, **kwargs):
        self.matched = {k: kwargs[k] for k in self.vars if k in kwargs}

        """self.solve_graph.add_vertices(len(self.vars))
        self.solve_graph.vs["names"] = self.vars
        for identity, equation in self.equations.items():
            target_index = self.vars.index(identity[0])
            print(identity)
            for item in list(identity[1]):
                if item == identity[0]:
                    continue
                self.solve_graph.add_edge(target_index, self.vars.index(item))
                self.solve_graph.es[-1]["identity"] = identity

        print(self.solve_graph.get_all_simple_paths(3, 1))
        print(self.solve_graph.vs["names"])"""


        print(f"Created {self}")

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join([f'{q}: {v}' for q, v in self.matched.items()])})"

    def solve(self, target):
        known = frozenset([k for k in self.matched])

        unknown_values = {}
        for identity, equation in self.equations.items():
            unknown_values[identity] = frozenset([i for i in list(identity) if i not in known])

        solve_graph = {}
        while target not in known:
            viewed_pairs = {}
            tbr = []
            if not unknown_values:
                raise ValueError(f"{self.__class__.__name__} could not find {target}")
            for i, v in unknown_values.items():
                if len(v) <= 1:
                    solve_graph[v] = [i]
                    tbr.append(i)
                elif v in viewed_pairs:
                    viewed_pairs[v].append(i)
                    tbr += viewed_pairs[v]
                    if len(viewed_pairs[v]) == len(v):
                        solve_graph[v] = viewed_pairs[v]
                        viewed_pairs.pop(v)
                else:
                    viewed_pairs[v] = [i]
            [unknown_values.pop(v) for v in tbr]
            known = set(known)
            for item in solve_graph:
                known = known.union(item)

            known = frozenset(known)

            for identity, equation in unknown_values.items():
                unknown_values[identity] = frozenset([i for i in list(identity) if i not in known])

        for item, value in solve_graph.items():
            precursors = set([q for w in [[i for i in list(v) if i not in item] for v in value] for q in w])
            solve_graph[item] = (precursors, value)

        nodes = set()
        for i, v in solve_graph.items():
            nodes.add(frozenset(i))
            nodes.add(frozenset(v[0]))
        nodes = list(nodes)
        graph = ig.Graph()
        graph.add_vertices(len(nodes))
        for i, v in solve_graph.items():
            graph.add_edge(nodes.index(frozenset(v[0])), nodes.index(frozenset(i)))
        start_node_candidates = [node for node in nodes if node.issubset(set(self.matched.keys()))]

        target_node_candidates = [node for node in nodes if target in node]
        assert target_node_candidates
        assert start_node_candidates

        start_node = start_node_candidates[0]
        target_node = target_node_candidates[0]
        path = graph.get_shortest_paths(v=nodes.index(start_node), to=nodes.index(target_node))
        assert path
        path = path[0]

        solve_graph = {(i, frozenset(v[0])): v[1] for i, v in solve_graph.items()}

        path = [nodes[p] for p in path][::-1]
        equation_path = []
        current = path.pop(0)
        for p in path:
            equation_path.append([(self.equations[q], q) for q in solve_graph[(current, p)]])
            current = p
        equation_path = equation_path[::-1]
        return self.pathsolve(equation_path, target)

    def pathsolve(self, path, target):
        knowns = set(self.matched.keys())
        temp_matches = self.matched.copy()

        for item in path:
            solve_targets = []
            for sub in item:
                solve_targets += [i for i in sub[1] if i not in knowns]
            solve_targets = set(solve_targets)
            if len(solve_targets) != len(item):
                raise ValueError(f"Cannot simultaneous solve {item}, knowing {knowns}")
            if len(item) == 1:
                temp_matches[list(solve_targets)[0]] = self.iterative_solve(item[0][0], list(solve_targets)[0], temp_matches)
            else:
                result = self.multi_iterative_solve([i[0] for i in item],  # equation
                                                    list(solve_targets), temp_matches)  # Target, known vals
                temp_matches.update(result)
            knowns.update(solve_targets)
        return temp_matches[target]

    def multi_iterative_solve(self, equation, target_name, knowns=None):
        knowns = self.matched if knowns is None else knowns
        if set(target_name).issubset(set(knowns)):
            return {v: knowns[v] for v in target_name}

        output = {t: random() for t in target_name}

        temps = knowns.copy()
        for q in range(100):  # Multidimensional newtons method
            temps.update(output)
            fx = [e(temps) for e in equation]
            fx = np.matrix(fx).T

            dx = [[(e({**temps, **{t: temps[t] + 0.001}}) - e({**temps, **{t: temps[t] - 0.001}}))/0.002 for t in target_name] for e in equation]
            dx = np.matrix(dx)
            output_vec = np.matrix(list(output.values())) - np.dot(np.linalg.inv(dx), fx).T
            output = {t: output_vec.item(0, i) for i, t in enumerate(target_name)}

            if not q % 50:
                print(f"Iter {q}: x={output}, f={fx}, d={dx}")
        print(f"Iter {q}: x={output}, f={fx}, d={dx}")
        print("-"*20)
        return {t: round(v, 6) for t, v in output.items()}

    def iterative_solve(self, equation, target_name, knowns=None):
        knowns = self.matched if knowns is None else knowns

        q = -1
        fx = None
        dx = None
        # newton solve
        guess = random()
        temp_known = knowns.copy()
        for q in range(100):
            temp_known[target_name] = guess
            fx = equation(temp_known)
            # if abs(fx) <= 1e-10:
            #    break

            temp_known[target_name] = guess + 0.001
            dx = equation(temp_known)
            if dx == 0:
                break

            temp_known[target_name] = guess - 0.001
            dx = (dx - equation(temp_known)) / 0.002
            guess -= fx/dx
            if not q % 50:
                print(f"Iter {q}: x={guess}, f={fx}, d={dx}")
        print(f"Iter {q}: x={guess}, f={fx}, d={dx}")
        print("-" * 20)
        return round(guess, 6)

    def __getattr__(self, item):
        if item not in self.vars:
            raise AttributeError(f"{self.__class__.__name__} does not recognise {item}")
        if item in self.matched:
            return self.matched[item]
        return self.solve(item)

    def get_base_template(self):
        return("""super().__init__()
        self.vars = ["x", "y", "mag", "angle"]
        self.equations = {frozenset(["x", "y", "mag"]): (lambda i: (i["x"] ** 2 + i["y"] ** 2) ** 0.5 - i["mag"]),
                          frozenset(["x", "angle", "mag"]): (lambda i: (i["x"] / math.cos(math.radians(i["angle"]))) - i["mag"]),
                          frozenset(["y", "angle", "mag"]): (lambda i: (i["y"] / math.sin(math.radians(i["angle"]))) - i["mag"])}

        self.finish_init(**kwargs)""")