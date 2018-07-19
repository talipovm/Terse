import re
from Grammar.LineCommandFactory import LineCommandFactory
from Grammar.Top_Grammar import Top_Grammar
from Grammar.Functions import ExpressionFactory


class GlobalCommand_Troublemaker(Top_Grammar):
    def __init__(self, GI, FI, parsed_container):
        super().__init__(GI, FI, parsed_container)
        self.preprocess()

    def preprocess(self):
        s_GI = self.GI.s
        s_re = re.search(r'troublemaker\s+(.*):', s_GI)
        if s_re is None:
            raise SyntaxError
        self.ptn = ExpressionFactory(s_re.group(1)).assign()
        self.commands = self.get_enclosed_commands()

    def match(self, s_FI):
        return self.ptn.match(s_FI)

    def get_enclosed_commands(self):
        out = []
        for s_grammar in self.GI:
            s = s_grammar.lstrip().split('#')[0]
            if s[:15]=='endtroublemaker':
                break
            cmd = LineCommandFactory(self.GI, self.FI, self.parsed_container, self.troublemakers).assign()
            out.append(cmd)
        return out

    def execute(self):
        for cmd in self.commands:
            cmd.execute()