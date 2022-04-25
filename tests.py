from baseitem import BaseItem


class Test(BaseItem):
    def __init__(self):
        kwargs = {"a": 1}
        super().__init__()
        self.vars = ["a", "b", "c", ""]
        self.equations = {frozenset(["a", "b"]): (lambda i: i['a'] + 1 - i["b"]),
                          frozenset(["b", "c"]): (lambda i: i['c'] / 2 - i["b"])}

        self.finish_init(**kwargs)
        assert self.solve("c") == 4
        print("-" * 20)
        print("Passed all tests")
        print("-" * 20)