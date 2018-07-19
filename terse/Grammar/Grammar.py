import re
from Grammar.GlobalCommand_If import GlobalCommand_If
from Grammar.GlobalCommand_Troublemaker import GlobalCommand_Troublemaker
from Containers.ParsedStructure import ParsedContainer
from collections import defaultdict
from Grammar.Top_Grammar import Top_Grammar

import logging
log = logging.getLogger(__name__)

use_datrie = False
if use_datrie:
    import datrie
    import string
else:
    from Tools.trie import Trie

class Grammar(Top_Grammar):
    def __init__(self, GI=None, FI=None):
        super().__init__(GI,FI,None,None)
        self.parsed_container = ParsedContainer()

        self.patterns = None
        self.patterns0 = None
        self.troublemakers = []
        self.init_grammar()

        self.patterns_pos = self.patterns['substring with position']
        self.patterns_regex = self.patterns['regex']

        if use_datrie:
            self.datrie = datrie.Trie(string.printable)
            for w,p in self.patterns0.items():
                self.datrie[w] = p
            self.find = self.find_datrie
        else:
            self.trie = Trie(self.patterns0)
            self.find = self.find_trie

    def init_grammar(self):
        self.patterns = defaultdict(list)
        self.patterns0 = defaultdict(dict)
        for s_full in self.GI:
            s = s_full.split('#')[0]
            if re.search('^if',s):
                p = GlobalCommand_If(self.GI, self.FI, self.parsed_container, self.troublemakers)
                if p.pattern_type=='substring with position 0':
                    self.patterns0[p.pattern] = p
                else:
                    self.patterns[p.pattern_type].append(p)
            elif re.search('^troublemaker',s):
                p = GlobalCommand_Troublemaker(self.GI, self.FI, self.parsed_container)
                self.troublemakers.append(p)

    def find_datrie(self, s):
        found = self.datrie.prefix_values(s)
        if found:
            return found[0]
        for p in self.patterns_regex:
            if p.pattern.search(s) is not None:
                return p
        for p in self.patterns_pos:
                if s[p.start:p.end]==p.pattern:
                    return p

    def find_trie(self, s):
        found = self.trie.find(s)
        if found is not None:
            return self.patterns0[found]
        for p in self.patterns_regex:
            if p.pattern.search(s) is not None:
                return p
        for p in self.patterns_pos:
            if s[p.start:p.end]==p.pattern:
                return p

    def find_brute_force(self, s):
        for p in self.patterns0.values():
            if s[0:p.end] == p.pattern:
                return p
        for p in self.patterns_regex:
            if p.pattern.search(s) is not None:
                return p
        for p in self.patterns_pos:
            if s[p.start:p.end]==p.pattern:
                return p

    def parse(self):
        for s_FI in self.FI:
            p = self.find(s_FI)
            if p is not None:
                p.execute()
