import re
from Grammar.Top_Grammar import Top_Grammar
from Grammar.Functions import ExpressionFactory

import logging
log = logging.getLogger(__name__)

class Command_If(Top_Grammar):
    def __init__(self, GI, FI, parsed_container, troublemakers):
        super().__init__(GI, FI, parsed_container, troublemakers)

        self.pattern_type = None
        self.start = None
        self.end = None
        self.pattern = None
        self.commands = []
        self.preprocess(self.GI.s)

    def preprocess(self, s):
        s_GI = self.GI.s
        s_re = re.search(r'if\s+(.*):', s_GI) # syntax "if /xxx/:"
        if s_re is None:
            raise SyntaxError
        self.ptn = ExpressionFactory(s_re.group(1)).assign()
        self.commands = self.get_enclosed_commands()

    def get_enclosed_commands(self):
        out = []
        for s_grammar in self.GI:
            s = s_grammar.lstrip().split('#')[0]
            if s[:5]=='endif':
                break
            from Grammar.LineCommandFactory import LineCommandFactory # it has to be here to avoid import recursion
            cmd = LineCommandFactory(self.GI, self.FI, self.parsed_container, self.troublemakers).assign()
            out.append(cmd)
        return out

    def find(self, s_FI):
        return self.ptn.match(s_FI)

    def execute(self):
        if self.find(self.FI.s):
            out = None
            for cmd in self.commands:
                out = cmd.execute()
            return out