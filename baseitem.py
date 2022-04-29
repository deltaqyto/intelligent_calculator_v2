import igraph as ig
import numpy as np
from random import random


class BaseItem:
    def __init__(self):
        self.vars = []
        self.equations = {}
        self.matched = {}
        self.silent = False

    def finish_init(self, **kwargs):
        if "silent" in kwargs:
            self.silent = kwargs.pop("silent")
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

        if not self.silent:
            print("-"*20)
            print(f"Created {self}")

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join([f'{q}: {v}' for q, v in self.matched.items()])})"

    def solve(self, target):
        knowns = set([k for k in self.matched])

        equations = {identity: (frozenset([i for i in identity if i not in knowns]), equation) for identity, equation in self.equations.items()}

        solve_list = []
        while target not in knowns:     # This section does not pass test 2. Keys need to be the full io of the function
            print(knowns)
            viewed_pairs = {}
            clear_list = []

            for header, group in equations.items():
                unknowns, equation = group
                eq_knowns = frozenset([f for f in header if f in knowns])
                if eq_knowns.issubset(knowns) and eq_knowns:
                    solve_list.append((eq_knowns, unknowns, equation))
                    clear_list.append(header)

            for item in clear_list:
                knowns = knowns.union(equations[item][0])
                equations.pop(item)

            for item in equations:
                equations[item] = (frozenset([i for i in item if i not in knowns]), equations[item][1])

        solve_nodes = set()
        solve_edges = {}

        for start, end, item in solve_list:
            solve_nodes.add(start)
            solve_nodes.add(end)
            if end not in solve_edges:
                solve_edges[end] = [(start, item)]
            else:
                solve_edges[end].append((start, item))

        solve_nodes = list(solve_nodes)
        #print(solve_nodes, solve_edges)

        # Find a valid start and end candidate
        start_candidates = []
        end_candidates = []
        knowns = [k for k in self.matched]
        for end, starts in solve_edges.items():
            for start, _ in starts:
                if start.issubset(knowns):
                    start_candidates += (start, end)
            if target in end:
                end_candidates.append(end)

        assert start_candidates
        assert end_candidates

        graph = ig.Graph()
        graph.add_vertices(len(solve_nodes))
        for end, starts in solve_edges.items():
            for start, _ in starts:
                graph.add_edge(solve_nodes.index(start), solve_nodes.index(end))

        # Use the edge dict and find a path
        path = graph.get_shortest_paths(v=solve_nodes.index(start_candidates[0]),
                                        to=solve_nodes.index(end_candidates[0]))
        path = path[0]

        # Hand off each step to the solver
        cached_results = self.matched.copy()
        current_node = path[0]
        for step in path[1:]:            # be careful, this is not really tested
            eq = [v[1] for v in solve_edges[solve_nodes[step]]]  # Get equation from step     ,  if v[0] == solve_nodes[current_node]
            print(eq[0])
            if type(eq[0]) == tuple:
                cached_results[list(solve_nodes[step])[0]] = self.object_iterative_solve([eq[0][0], eq[0][2]], eq[0][1], cached_results)
            else:
                cached_results.update(self.iterative_solve(eq, solve_nodes[step], cached_results))
            current_node = step
        return cached_results[target]






        """            for identity, group in equations.items():
                unknowns, equation = group
                print(identity, unknowns)
                if unknowns not in viewed_pairs:
                    viewed_pairs[unknowns] = []
                viewed_pairs[unknowns].append((identity, equation))
                if len(unknowns) == len(viewed_pairs[unknowns]):
                    clear_list += viewed_pairs[unknowns]
                    solve_bindings[unknowns] = viewed_pairs[unknowns]
            [equations.pop(c[0]) for c in clear_list]
            for v in solve_bindings:
                knowns = knowns.union(v)
            equations = {identity: (frozenset([i for i in identity if i not in knowns]), equation[1]) for identity, equation in equations.items()}
"""
        """for header, group in solve_bindings.items():
            solve_bindings[header] = [frozenset([v for i in [list(g[0]) for g in group] for v in i]), group]

        print(solve_bindings)

        unique_values = list(set([a for b in [[header, frozenset([g for g in group[0] if g not in header])] for header, group in solve_bindings.items()] for a in b]))  # Demon comprehension -> collects a list of all unique groups of variables
        print(unique_values)

        graph = ig.Graph()
        graph.add_vertices(len(unique_values))
        for header, group in solve_bindings.items():
            graph.add_edge(unique_values.index(header), unique_values.index(frozenset([g for g in group[0] if g not in header])))

        start_node_candidates = [node for node in unique_values if node.issubset(set(self.matched.keys()))]

        target_node_candidates = [node for node in unique_values if target in node]
        assert target_node_candidates
        assert start_node_candidates

        start_node = start_node_candidates[0]
        target_node = target_node_candidates[0]
        path = graph.get_shortest_paths(v=unique_values.index(start_node), to=unique_values.index(target_node))
        assert path
        path = [unique_values[p] for p in path[0]]
        print(path)

        current = path.pop(0)
        result = []
        while path:
            item = path.pop(0)
            print(current, item)
            current = item"""


    def object_iterative_solve(self, equation, intermediates, knowns=None):
        if not equation:
            print("Equations not provided")
            return knowns
        knowns = self.matched if knowns is None else knowns

        output = {t: random() for t in intermediates}

        temps = knowns.copy()
        for q in range(100):  # Multidimensional newtons method
            temps.update(output)
            base_obj = equation[0](temps)
            fx = [e(base_obj, temps) for e in equation[1]]
            fx = np.matrix(fx).T

            dx = [[(e(equation[0]({**temps, **{t: temps[t] + 0.001}}), {**temps, **{t: temps[t] + 0.001}}) -
                    e(equation[0]({**temps, **{t: temps[t] - 0.001}}), {**temps, **{t: temps[t] - 0.001}}))/0.002
                   for t in intermediates] for e in equation[1]]
            dx = np.matrix(dx)

            # a non invertible matrix could be improper equation selection or the derivative == 0 prematurely
            output_vec = np.matrix(list(output.values())) - np.dot(np.linalg.inv(dx), fx).T
            output = {t: output_vec.item(0, i) for i, t in enumerate(intermediates)}

            if not q % 50 and not self.silent:
                print(f"Iter {q}: x={output}, \nf={fx}, \nd={dx}\n")
        if not self.silent:
            print(f"Iter {q + 1}: x={output}, \nf={fx}, \nd={dx}\n")
            print("-"*20)
        temps.update(output)
        return equation[0](temps)

    def iterative_solve(self, equation, target_name, knowns=None):
        if not equation:
            print("Equations not provided")
            return knowns
        knowns = self.matched if knowns is None else knowns
        if target_name in set(knowns):
            return {v: knowns[v] for v in target_name}

        output = {t: random() for t in target_name}

        temps = knowns.copy()
        for q in range(100):  # Multidimensional newtons method
            temps.update(output)
            fx = [e(temps) for e in equation]
            fx = np.matrix(fx).T

            dx = [[(e({**temps, **{t: temps[t] + 0.001}}) - e({**temps, **{t: temps[t] - 0.001}}))/0.002 for t in target_name] for e in equation]
            dx = np.matrix(dx)

            # a non invertible matrix could be improper equation selection or the derivative == 0 prematurely
            output_vec = np.matrix(list(output.values())) - np.dot(np.linalg.inv(dx), fx).T
            output = {t: output_vec.item(0, i) for i, t in enumerate(target_name)}

            if not q % 50 and not self.silent:
                print(f"Iter {q + 1}: x={output}, \nf={fx}, \nd={dx}\n")
        if not self.silent:
            print(f"Iter {q + 1}: x={output}, \nf={fx}, \nd={dx}\n")
            print("-"*20)
        return {t: round(v, 6) for t, v in output.items()}

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