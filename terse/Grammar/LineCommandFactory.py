from Grammar.Command_If import Command_If
from Grammar.Command_Jump import Command_Jump
from Grammar.Command_SafeJump import Command_SafeJump
from Grammar.Command_Table import Command_Table
from Grammar.Command_Assign import Command_Assign
from Grammar.Top_Grammar import Top_Grammar

import logging
log = logging.getLogger(__name__)

class LineCommandFactory(Top_Grammar):
    def __init__(self, GI, FI, parsed_container, troublemakers):
        super().__init__(GI, FI, parsed_container, troublemakers)

        s = self.GI.s.lstrip()
        if s[:2]=='if':
            self.CmdClass = Command_If
        elif s[:4]=='jump':
            self.CmdClass = Command_Jump
        elif s[:8]=='safejump':
            self.CmdClass = Command_SafeJump
        elif s[:5]=='table':
            self.CmdClass = Command_Table
        elif '=' in s:
            self.CmdClass = Command_Assign
        else:
            raise SyntaxError

    def assign(self):
        return self.CmdClass(self.GI, self.FI, self.parsed_container, self.troublemakers)