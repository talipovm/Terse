from Top import Top
import re
from Tools.calculator import Calculator
from Tools.misc import strip_all, get_range

class Functions(Top):

    def __init__(self, FI, get_params):
        self.FI = FI
        self.get_params = get_params
        self.compiled = {}

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
        c = Calculator(get_params=lambda x: int(self.get_params(x)))
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
        fields = strip_all(self.FI.s.split())
        return [fields[v-1] for v in get_range(s)]

    def parse(self, s_function):
        s=''
        if s_function[0] + s_function[-1] == '//':
            i, j = 1, -1
            return 'regex',self.function_regexp(s_function[i:j])

        if s_function[0] + s_function[-1] == "\'\'":
            i, j = 1, -1
            return 'string',self.function_string(s_function[i:j])

        if s_function[0] + s_function[-1] == '()':
            i, j = 1, -1
            return 'numeric_expression',self.function_expression(s_function[i:j])

        if s_function.find('field')==0:
            i, j = 5+1, -1
            return 'field',self.function_field(s_function[i:j])

        if s_function.find('characters')==0:
            i, j = 10+1, -1
            return 'char',self.function_characters(s_function[i:j])
