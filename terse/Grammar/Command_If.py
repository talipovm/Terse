import re

from Top import Top


class Command_If(Top):
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

        self.preprocess(s)

    def preprocess(self, s):
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
            self.pattern_type = 'substring with position'
            self.start = start
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
            from Grammar.LineCommandFactory import LineCommandFactory # it has to be here to avoid import recursion
            cmd = LineCommandFactory(self.GI, self.FI, self.fn, self.parsed_container, s)
            out.append(cmd)
        return out

    def find(self, s):
        if self.pattern_type=='regex':
            if self.pattern.search(s) is not None:
                return True
        if self.pattern_type=='substring with position':
            if s[self.start:self.end]==self.pattern:
                return True
        return False

    def execute(self):
        if self.find(self.FI.s):
            out = None
            for cmd in self.commands:
                out = cmd.execute()
            return out