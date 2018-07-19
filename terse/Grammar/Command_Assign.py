from Containers.ParsedStructure import ParsedElement
from Tools.misc import strip_all
from Grammar.Top_Grammar import Top_Grammar
from Grammar.Functions import ExpressionFactory

import logging
log = logging.getLogger(__name__)

class Command_Assign(Top_Grammar):
    def __init__(self, GI, FI, parsed_container, troublemakers):
        super().__init__(GI, FI, parsed_container, troublemakers)

        s = self.GI.s
        v = s.split('=', maxsplit=1)
        s_keys, s_function = strip_all(v)

        self.keys = strip_all(s_keys.split(','))
        self.f = ExpressionFactory(s_function,f_get_params=self.parsed_container.last_value).assign()

    def execute(self):
        vals = self.f.get_value(self.FI.s)

        if vals is None: # expression was not found
            return

        if self.keys == ['row']:     # are we parsing a table row?
            return vals

        if len(self.keys) != len(vals):
            raise SyntaxError

        for key, val in zip(self.keys,vals):
            assigned_element = ParsedElement(key, val)
            self.parsed_container.append(assigned_element)