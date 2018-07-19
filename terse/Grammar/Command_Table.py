import re
from Containers.ParsedStructure import ParsedElement
from Tools.misc import strip_all
from Grammar.Top_Grammar import Top_Grammar

import logging
log = logging.getLogger(__name__)

class Command_Table(Top_Grammar):
    def __init__(self, GI, FI, parsed_container, troublemakers):
        super().__init__(GI, FI, parsed_container, troublemakers)
        self.condition = None
        self.key = None
        self.mode = None
        self.commands = []

        s = self.GI.s
        self.preprocess(s)

    def preprocess(self,s):
        """
            var_name,run_until=/REGEXP/ | run_while=/REGEXP/
        (       LINE_BY_LINE_COMMAND\n)+
        """
        s_re = re.search(r'table\((.*)\):', s) # syntax "if /xxx/:"
        if s_re is None:
            raise SyntaxError
        s = s_re.group(1)
        if not (',' in s):
            raise SyntaxError
        s = strip_all(s.split(','))
        self.key = s[0]

        s = s[1]
        if not ('=' in s):
            raise SyntaxError
        mode, regexp = s.split('=',maxsplit=1)

        if not (mode in ['run_until', 'run_while']):
            raise SyntaxError
        self.mode = mode
        self.condition = regexp[1:-1]

        self.commands = self.get_enclosed_commands()

    def get_enclosed_commands(self):
        out = []
        for s_grammar in self.GI:
            s = s_grammar.lstrip()
            if s[:8]=='endtable':
                break
            from Grammar.LineCommandFactory import LineCommandFactory
            cmd = LineCommandFactory(self.GI, self.FI, self.parsed_container, self.troublemakers).assign()
            out.append(cmd)
        return out

    def execute(self):
        table = []
        try:
            while True:
                for cmd in self.commands:
                    row = cmd.execute()
                    if row:
                        table.append(row)

                # has the table end been reached?
                if self.mode == 'run_until':
                    if self.condition == '':
                        if self.FI.s.strip() == '':
                            break
                    else:
                        if re.search(self.condition, self.FI.s) is not None:
                            break

                elif self.mode == 'run_while':
                    if re.search(self.condition, self.FI.s) is None:
                        break
        except StopIteration:
            pass
        if len(table)>0:
            assigned_element = ParsedElement(self.key, table)
            self.parsed_container.append(assigned_element)