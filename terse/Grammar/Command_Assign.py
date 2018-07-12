from Containers.ParsedStructure import ParsedElement
from Tools.misc import strip_all
from Top import Top


class Command_Assign(Top):
    def __init__(self, GI, FI, fn, parsed_container, s):
        super().__init__()
        self.GI = GI
        self.FI = FI
        self.fn = fn
        self.parsed_container = parsed_container

        v = s.split('=', maxsplit=1)
        s_keys, s_function = strip_all(v)

        self.keys = strip_all(s_keys.split(','))
        self.s_function = s_function

    def execute(self):
        expr_type,vals = self.fn.parse(self.s_function)

        if vals is None: # expression was not found
            return

        if self.keys == ['row']:     # are we parsing a table row?
            return vals

        if len(self.keys) != len(vals):
            raise SyntaxError

        # Assign
        for key, val in zip(self.keys,vals):
            assigned_element = ParsedElement(key, val)
            self.parsed_container.append(assigned_element)