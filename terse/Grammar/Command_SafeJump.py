import re
from Grammar.Top_Grammar import Top_Grammar
from Grammar.Functions import ExpressionFactory

import logging
log = logging.getLogger(__name__)

class Command_SafeJump(Top_Grammar):
    def __init__(self, GI, FI, parsed_container, troublemakers):
        super().__init__(GI, FI, parsed_container, troublemakers)

        s = self.GI.s
        s_re = re.search(r'safejump\s*(.*)', s)
        if s_re is None:
            raise SyntaxError

        self.s_function = s_re.group(1)
        self.f = ExpressionFactory(self.s_function,f_get_params=self.parsed_container.last_value).assign()

    def execute(self):
        if not (self.f.type in ('numeric_expression','regex')):
            raise SyntaxError
        while not self.f.match(self.FI.s):
            next(self.FI)
            for troublemaker in self.troublemakers:
                if troublemaker.match(self.FI.s):
                    troublemaker.execute()
