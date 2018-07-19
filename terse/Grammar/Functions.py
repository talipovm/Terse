import re
from Tools.calculator import Calculator
from Tools.misc import strip_all, get_range
from Grammar.Top_Grammar import Top_Grammar
from Top import Top

class ExpressionFactory(Top_Grammar):

    def __init__(self, s_GI, f_get_params=None):
        self.s_GI = s_GI
        self.f_get_params = f_get_params
        if s_GI[0] + s_GI[-1] == '//':
            self.PtnClass = Expression_regex
        elif s_GI[0] + s_GI[-1] == "\'\'":
            self.PtnClass = Expression_string
        elif s_GI[0] + s_GI[-1] == "()":
            self.PtnClass = Expression_arithmetics
        elif s_GI.find('field')==0:
            self.PtnClass = Expression_field
        elif s_GI.find('characters')==0:
            self.PtnClass = Expression_character
        elif re.search(r'\[\S+\]\'.*\'', s_GI):
            self.PtnClass = Expression_positional
        else:
            raise SyntaxError

    def assign(self):
        return self.PtnClass(self.s_GI,self.f_get_params)


class Expression_regex(Top):
    def __init__(self, s_GI, f_get_params=None):
        super().__init__()
        self.type = 'regex'
        i, j = 1, -1
        self.pattern = re.compile(s_GI[i:j])

    def match(self, s_FI):
        return self.pattern.search(s_FI) is not None

    def get_value(self, s_FI):
        found = self.pattern.search(s_FI)
        if found is None:
            return None
        else:
            return found.groups()


class Expression_positional(Top):
    def __init__(self, s_GI, f_get_params=None):
        super().__init__()
        s_re = re.search(r'\[(\S+)\]\'(.*)\'', s_GI) # syntax "if [N]'xxx'"
        try:
            start = int(s_re.group(1))
        except (ValueError,TypeError):
            raise SyntaxError
        self.type = 'substring with position'
        self.start = start
        self.pattern = s_re.group(2)
        self.end = start + len(self.pattern)

    def match(self, s_FI):
        return s_FI[self.start:self.end]==self.pattern

    def get_value(self, s_FI=None):
        raise NotImplementedError


class Expression_string(Top):
    def __init__(self, s_GI, f_get_params=None):
        super().__init__()
        self.type = 'string'
        i, j = 1, -1
        self.expression = s_GI[i:j]

    def match(self, s_FI):
        raise NotImplementedError

    def get_value(self, s_FI=None):
        return [self.expression]


class Expression_arithmetics(Top):
    def __init__(self, s_GI, f_get_params):
        super().__init__()
        self.type = 'numeric_expression'
        i, j = 1, -1
        self.expression = s_GI[i:j]
        self.f_get_params = f_get_params
        self.calc = Calculator(get_params=lambda x: self.f_get_params(x))

    def match(self, s_FI):
        raise NotImplementedError

    def get_value(self, s_FI=None):
        try:
            out = self.calc.ev(self.expression)
        except:
            return ''
        return [str(out)] # TODO think about types


class Expression_field(Top):
    def __init__(self, s_GI, f_get_params=None):
        super().__init__()
        self.type = 'field'
        i, j = 5+1, -1
        self.expression = s_GI[i:j]
        self.ranges = get_range(self.expression)

    def match(self, s_FI):
        raise NotImplementedError

    def get_value(self, s_FI=None):
        fields = strip_all(s_FI.split())
        return [fields[v-1] for v in self.ranges]


class Expression_character(Top):
    def __init__(self, s_GI, f_get_params=None):
        super().__init__()
        self.type = 'characters'
        i, j = 10+1, -1
        self.expression = s_GI[i:j]

        self.ranges = []
        for s_range in strip_all(self.expression.split(',')):
            v = re.search('\[(\S+)-(\S+)\]',s_range).groups()
            i = int(v[0])-1
            j = int(v[1])
            if i > j:
                raise SyntaxError
            self.ranges.append([i,j])

    def match(self, s_FI):
        raise NotImplementedError

    def get_value(self, s_FI=None):
        res = []
        for i,j in self.ranges:
            if j >= len(s_FI):
                break
            res.append(s_FI[i:j])
        return res