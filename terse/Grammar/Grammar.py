from Top import Top
import re
from Tools.calculator import Calculator
from Tools.misc import strip_all
import copy
from Containers.ParsedStructure import ParsedContainer, ParsedElement

import logging
log = logging.getLogger(__name__)

if __name__ == "__main__":
    import sys
    sys.path.append('..')

class Grammar(Top):
    def __init__(self, GI=None, FI=None):
        super().__init__()
        self.GI = self.init_grammar(GI)
        self.FI = FI
        self.parsed = ParsedContainer()
        self.field_separator = ' '
        self.table_mode = False
        self.indentation = 4
        self.depth = 0
        self.repeat_loop = False
        self.stop_line_parsing_on_first_match = True
        self.compiled = {}
        return

    def init_grammar(self, GI):
        """
        Read in grammar file, remove comments and empty lines
        :param GI:
        :return:
        """
        res = []
        for s_full in GI:
            s_nocomment = s_full.split('#')[0]
            if re.search('^\s*$', s_nocomment) is None:
                res.append(s_nocomment)
        return res

    def get_range(self, s):
        """
        Takes a string of format [RANGE] and expands RANGE into the list of ints
        :param s:
        :return:
        """
        s_range = strip_all(s.split(','))
        v_res = []
        for s_element in s_range:
            if '-' in s_element:
                v = s_element.split('-')
                i = int(v[0])
                j = int(v[1])
                if i > j:
                    raise SyntaxError
                for k in range(i,j+1):
                    v_res.append(k)
            else:
                i = int(s_element)
                v_res.append(i)
        return v_res

    def function_regexp(self, s):
        """
        Evaluates REGEXP
        :param s:
        :return: None if nothing found
        """
        if s not in self.compiled:
            self.compiled[s] = re.compile(s)
        found = self.compiled[s].search(self.FI.s)
        #found = re.search(s, self.FI.s)
        if found is None:
            return None
        else:
            return found.groups()

    def function_string(self, s):
        """
        Returns STRING
        :param s:
        :return: The string itself
        """
        return [s]

    def function_expression(self, s):
        """
        Evaluates EXPRESSION
        :param s:
        :return:
        """
        # Construct a list with the latest values of self.parsed of int type
        c = Calculator(params=self.parsed.int_values())

        try:
            out = c.ev(s)
        except:
            return ''
        return str(out) # TODO think about types

    def function_characters(self, s):
        """
        returns substrings defined by the character positions
        :param s:
        :return:
        """
        s_ranges = strip_all(s.split(','))

        res = []
        for s_range in s_ranges:
            v = re.search('\[(\S+)-(\S+)\]',s_range).groups()
            i = int(v[0])-1
            j = int(v[1])
            if i > j:
                raise SyntaxError
            if j >= len(self.FI.s):
                break
            res.append(self.FI.s[i:j])
        return res

    def function_field(self, s):
        """
        Extracts fields
        :param s:
        :return:
        """
        v_res = self.get_range(s)
        #
        fields = strip_all(self.FI.s.split())
        #
        res = []
        for v in v_res:
            res.append(fields[v-1])
        return res

    @staticmethod
    def count_leading_white_spaces(s):
        for i in range(len(s)):
            if s[i] != ' ':
                return i

    def is_intended_properly(self, s):
        observed = self.count_leading_white_spaces(s)
        expected = self.indentation*self.depth
        return observed == expected

    def line_by_line_command_jump(self, s):
        try:
            n = int(s)
            self.FI.skip_n(n)
        except (TypeError, ValueError):
            self.FI.skip_until(pattern=s[1:-1], regexp=True)
        return

    def line_by_line_command_assign(self, s):
        return self.global_command_assign(s)

    def line_by_line_command_if(self, s):
        return self.global_command_if(s)

    def line_by_line_repeat(self):
        self.repeat_loop = True
        return

    def parse_line_by_line_command(self, s):

        s = s.strip()

        if s.find('jump')==0:                           # JUMP
            i, j = 4+1, -1
            self.line_by_line_command_jump(s[i:j])
            return []

        if s.find('if')==0:
            return self.line_by_line_command_if(s)

        if s.find('repeat')==0:
            self.line_by_line_repeat()
            return []

        if '=' in s:
            row = self.line_by_line_command_assign(s)
            return row

        return []

    def function_table(self, s):
        """
            run_until=/REGEXP/ | run_while=/REGEXP/
        (       LINE_BY_LINE_COMMAND\n)+
        """
        if not ('=' in s):
            raise SyntaxError
        mode, regexp = s.split('=',maxsplit=1)
        if not (mode in ['run_until', 'run_while']):
            raise SyntaxError
        regexp = regexp[1:-1]

        self.depth += 1
        table = []
        start_iter = copy.deepcopy(self.GI_iter)
        while True:
            # Has the stop criterion been met?
            if mode == 'run_until':
                if regexp == '':
                    if self.FI.s.strip() == '':
                        break
                else:
                    if re.search(regexp, self.FI.s) is not None:
                        break
            elif mode == 'run_while':
                if re.search(regexp, self.FI.s) is None:
                    break

            if self.repeat_loop:
                self.repeat_loop = False
                self.GI_iter = copy.deepcopy(start_iter)

            try:
                s_grammar = next(self.GI_iter)
                if self.is_intended_properly(s_grammar):
                    row = self.parse_line_by_line_command(s_grammar)
                    if row:
                        table.append(row)
            except StopIteration:
                break
        self.depth -= 1

        return [table]

    def parse_function(self, s_function):

        if s_function[0] + s_function[-1] == '//':               # REGEXP
            i, j = 1, -1
            return self.function_regexp(s_function[i:j])

        if s_function[0] + s_function[-1] == "\'\'":             # STRING
            i, j = 1, -1
            return self.function_string(s_function[i:j])

        if s_function[0] + s_function[-1] == '()':               # EXPRESSION
            i, j = 1, -1
            return self.function_expression(s_function[i:j])

        if s_function.find('characters')==0:                     # CHARACTERS
            i, j = 10+1, -1
            return self.function_characters(s_function[i:j])

        if s_function.find('field')==0:                          # FIELD
            i, j = 5+1, -1
            return self.function_field(s_function[i:j])

        if s_function.find('table')==0:                          # TABLE
            i, j = 5+1, -2
            return self.function_table(s_function[i:j])

        return

    def global_command_assign(self, s):
        v = s.split('=', maxsplit=1)

        s_keys, s_function = strip_all(v)

        # get the key names:
        keys = strip_all(s_keys.split(','))
        vals = self.parse_function(s_function)

        if vals is None: # expression was not found
            return

        if keys == ['row']:     # are we parsing a table row?
            return vals

        if len(keys) != len(vals):
            raise SyntaxError

        # Assign
        for key, val in zip(keys,vals):
            assigned_element = ParsedElement(key, val)
            self.parsed.append(assigned_element)

        return True # the pattern has matched

    def global_command_if(self, s):
        s_re = re.search(r'if\s+/(.*)/:', s) # syntax "if /xxx/:"
        if s_re is not None:
            if not self.function_regexp(s_re.group(1)):
                return

        s_re = re.search(r'if\s+\[(\S+)\]\'(.*)\':', s) # syntax "if [N]'xxx'"
        if s_re is not None:
            try:
                start = int(s_re.group(1))
                end = start + len(s_re.group(2))
            except (ValueError,TypeError):
                raise SyntaxError
            if self.FI.s[start:end]!=s_re.group(2):
                return
        else:
            return

        self.depth += 1
        out = []
        for s_grammar in self.GI_iter:
            if not self.is_intended_properly(s_grammar):
                break
            out.append(self.parse_line_by_line_command(s_grammar))
        self.depth -= 1
        if out:             # actually needed only for line_by_line_command_if, so the program design is messed up here; TODO
            if len(out)==1:
                return out[0]
            else:
                return out
        return

    def global_command_space_filler(self, s):
        # space_filler(start=/REGEXP/, nlines=(EXPRESSION))
        s_re = re.search(r'space_filler\((.*)\s*,\s*(.*)\)', s)
        if s_re is None:
            raise SyntaxError
        (start,nlines)=s_re.groups()

        if '=' in start:
            start = start.split('=',maxsplit=1)[1]
        start = start[1:-1] # remove //
        found = self.function_regexp(start)
        if found is None:
            return

        if '=' in nlines:
            nlines = nlines.split('=',maxsplit=1)[1]
        nlines = nlines[1:-1] # remove ()
        nskip = self.function_expression(nlines)

        try:
            n = int(nskip)
            self.FI.skip_n(n)
        except (ValueError,TypeError):
            pass

        return True # the pattern has matched


    def global_command_distractor(self, s):
        return False

    def parse_global_command(self, s):

        if not s:
            return

        if s[:2]=='if': # if
            return self.global_command_if(s)

        if s[:5]=='endif': # if
            return # probably we don't need it at all

        if 'space_filler' in s: # space_filler
            return self.global_command_space_filler(s)

        if 'distractor' in s: # distractor
            return self.global_command_distractor(s)

        if 'flag' in s: # flag
            return False # not implemented yet

        if '=' in s: # assign
            return self.global_command_assign(s)

        return False

    def parse(self):
        for _ in self.FI:
            self.GI_iter = self.GI.__iter__()
            for s_grammar in self.GI_iter:
                if not self.is_intended_properly(s_grammar):
                    continue
                try:
                    matched = self.parse_global_command(s_grammar)
                    if matched and self.stop_line_parsing_on_first_match:
                        break # go to the next line of FI
                except StopIteration: # EOF of (presumably) self.FI has been reached
                    return
        pass

#    def postprocess(self):
#        pass

#    def webdata(self):

if __name__ == "__main__":
    from Settings import Settings
    from Top import Top
    Top.settings = Settings()
    Top.settings.detailed_print = True

    from Tools.file2 import file2
    GI = file2('../../parsing-rules/gamess_parsing.txt')
    FI = file2('../../parsing-rules/Gamess/ZI1.gms')

    G = Grammar(GI,FI)
    G.parse()
    for item in G.parsed.data:
        data = str(item.data)
        if len(data)>50:
            data = data[:50]+'...'
        print(item.key, data )

    print(G)

    import pickle
    pickle.dump(G.parsed,open('../../G.p','wb'))