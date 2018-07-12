import re

from Top import Top


class Command_Jump(Top):
    def __init__(self, GI, FI, fn, parsed_container, s):
        super().__init__()
        self.GI = GI
        self.FI = FI
        self.fn = fn
        self.parsed_container = parsed_container

        s_re = re.search(r'jump\s*(.*)', s) # syntax "if /xxx/:"
        if s_re is None:
            raise SyntaxError

        self.s_function = s_re.group(1)

    def execute(self):
        expr_type,vals = self.fn.parse(self.s_function)
        if expr_type=='numeric_expression':
            n = int(vals[0])
            self.FI.skip_n(n)
        if expr_type=='regex':
            self.FI.skip_until(pattern=self.s_function[1:-1], regexp=True)