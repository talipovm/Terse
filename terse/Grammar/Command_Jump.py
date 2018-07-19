import re
from Grammar.Top_Grammar import Top_Grammar
from Grammar.Functions import ExpressionFactory

import logging
log = logging.getLogger(__name__)

class Command_Jump(Top_Grammar):
    def __init__(self, GI, FI, parsed_container, troublemakers):
        super().__init__(GI, FI, parsed_container, troublemakers)

        s = self.GI.s
        s_re = re.search(r'jump\s*(.*)', s) # syntax "if /xxx/:"
        if s_re is None:
            raise SyntaxError

        self.s_function = s_re.group(1)
        self.f = ExpressionFactory(self.s_function,f_get_params=self.parsed_container.last_value).assign()

    def execute(self):
        expr_type = self.f.type
        try:
            if expr_type=='numeric_expression':
                vals = self.f.get_value()
                if vals:
                    n = int(vals[0])
                    self.FI.skip_n(n)
                else:
                    log.debug('Numeric expression could not be evaluated')
            elif expr_type == 'string':
                vals = self.f.get_value()
                self.FI.skip_until_string(pattern=vals[0])
            elif expr_type=='regex':
                self.FI.skip_until_regex(pattern=self.f.pattern)
        except StopIteration:
            pass

