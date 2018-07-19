import re
from Grammar.LineCommandFactory import LineCommandFactory
from Grammar.Top_Grammar import Top_Grammar
from Grammar.Functions import ExpressionFactory


class GlobalCommand_If(Top_Grammar):
    def __init__(self, GI, FI, parsed_container, troublemakers):
        super().__init__(GI, FI, parsed_container, troublemakers)
        self.pattern_type = None
        self.start = None
        self.end = None
        self.pattern = None
        self.commands = []
        self.init_global_if()

    def init_global_if(self):
        s_GI = self.GI.s
        s_re = re.search(r'if\s+(.*):', s_GI) # syntax "if /xxx/:"
        if s_re is None:
            raise SyntaxError
        s_re = s_re.group(1)
        ptn = ExpressionFactory(s_re).assign()
        self.pattern_type = ptn.type
        self.pattern = ptn.pattern
        self.start = ptn.start
        self.end = ptn.end
        self.commands = self.get_enclosed_commands()
        if self.start == 0:
            self.pattern_type += ' 0'

    def get_enclosed_commands(self):
        out = []
        for s_grammar in self.GI:
            s = s_grammar.lstrip()
            if s[:5]=='endif':
                break
            cmd = LineCommandFactory(self.GI, self.FI, self.parsed_container, self.troublemakers).assign()
            out.append(cmd)
        return out

    def execute(self):
        for cmd in self.commands:
            cmd.execute()


class GlobalCommand_Troublemaker(Top_Grammar):
    pass
