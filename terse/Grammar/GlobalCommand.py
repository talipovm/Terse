import re
from Top import Top
from Grammar.LineCommandFactory import LineCommandFactory


class GlobalCommand(Top):
    def __init__(self, GI, FI, fn, parsed_container, s):
        super().__init__()
        self.GI = GI
        self.FI = FI
        self.fn = fn
        self.parsed_container = parsed_container
        self.pattern_type = None
        self.start = None
        self.end = None
        self.pattern = None
        self.commands = []
        self.init_global_if(s)

    def init_global_if(self, s):
        s_re = re.search(r'if\s+/(.*)/:', s) # syntax "if /xxx/:"
        if s_re is not None:
            self.pattern_type = 'regex'
            self.pattern = re.compile(s_re.group(1))
            self.commands = self.get_enclosed_commands()
            return

        s_re = re.search(r'if\s+\[(\S+)\]\'(.*)\':', s) # syntax "if [N]'xxx'"
        if s_re is not None:
            try:
                start = int(s_re.group(1))
                end = start + len(s_re.group(2))
            except (ValueError,TypeError):
                raise SyntaxError
            self.start = start
            self.pattern_type = 'substring with position'
            if self.start == 0:
                self.pattern_type += ' 0'
            self.end = end
            self.pattern = s_re.group(2)
            self.commands = self.get_enclosed_commands()
            return

        raise SyntaxError

    def get_enclosed_commands(self):
        out = []
        for s_grammar in self.GI:
            s = s_grammar.lstrip()
            if s[:5]=='endif':
                break
            cmd = LineCommandFactory(self.GI, self.FI, self.fn, self.parsed_container, s)
            out.append(cmd)
        return out

    def execute(self):
        for cmd in self.commands:
            cmd.execute()