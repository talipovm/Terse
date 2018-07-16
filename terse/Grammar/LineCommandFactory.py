
from Top import Top
import re


class LineCommandFactory(Top):
    def __init__(self, GI, FI, fn, parsed_container, s):
        super().__init__()
        self.GI = GI
        self.FI = FI
        self.fn = fn
        self.parsed_container = parsed_container
        self.cmd = None

        CmdClass = None
        if s[:2]=='if':
            from Grammar.Command_If import Command_If
            CmdClass = Command_If
        elif s[:4]=='jump':
            from Grammar.Command_Jump import Command_Jump
            CmdClass = Command_Jump
        elif s[:5]=='table':
            from Grammar.Command_Table import Command_Table
            CmdClass = Command_Table
        elif s[:12]=='space_filler':
            CmdClass = Command_Spacefiller
        elif '=' in s:
            from Grammar.Command_Assign import Command_Assign
            CmdClass = Command_Assign

        if CmdClass is None:
            raise SyntaxError

        self.cmd = CmdClass(self.GI, self.FI, self.fn, self.parsed_container, s)

    def execute(self):
        if self.cmd is not None:
            return self.cmd.execute()

class Command_Spacefiller(Top):
    def __init__(self, GI, FI, fn, parsed_container, s):
        super().__init__()
        self.GI = GI
        self.FI = FI
        self.fn = fn
        self.parsed_container = parsed_container

        # space_filler(start=/REGEXP/, nlines=(EXPRESSION))
        s_re = re.search(r'space_filler\((.*)\s*,\s*(.*)\)', s)
        if s_re is None:
            raise SyntaxError
        (start,nlines)=s_re.groups()

        if '=' in start:
            start = start.split('=',maxsplit=1)[1]
        self.start = start[1:-1]

        if '=' in nlines:
            nlines = nlines.split('=', maxsplit=1)[1]
        self.nlines = nlines[1:-1]  # remove ()

    def execute(self):
        found = self.fn.function_regexp(self.start)
        if found is None:
            return

        nskip = self.fn.function_expression(self.nlines)
        try:
            n = int(nskip)
            self.FI.skip_n(n)
        except (ValueError,TypeError):
            pass