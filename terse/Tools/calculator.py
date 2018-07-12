import math
from Top import Top

import logging
log = logging.getLogger(__name__)


class Calculator(Top):
    def __init__(self, params=None, get_params=None):
        super().__init__()
        self.function_names = ('ceiling', 'floor', '')
        self.functions = (math.ceil, math.floor, lambda x: x)

        self.arithm_names = ('+', '-', '*', '/')
        self.arithm_funs = ((lambda x, y: x + y),
                            (lambda x, y: x - y),
                            (lambda x, y: x * y),
                            (lambda x, y: x / y)
                            )
        if get_params is not None:
            self.get_params = get_params
        else:
            if params is not None:
                self.get_params = lambda x: params[x]


    @staticmethod
    def find_closing_parenthesis(s, i_start=0):
        depth = 0
        for i in range(i_start, len(s)):
            if s[i] == '(':
                depth += 1
            if s[i] == ')':
                depth -= 1
                if depth == 0:
                    return i

    def ev(self, s):
        if not s:  # to resolve - sign starting expression, as in negative numbers
            return 0

        if s[0] == '_':  # replace back _ by -
            s = '-' + s[1:]

        # Dow we still have a complex expression?
        try:
            return int(s)
        except ValueError:
            pass

        if s in self.params:  # variable substitution
            return self.params[s]

        for f_name, f in zip(self.function_names, self.functions):
            f_len = len(f_name)
            f_name += '('
            if f_name in s:
                i_start = s.find(f_name) + f_len
                i_end = self.find_closing_parenthesis(s, i_start)
                raw_res = self.ev(s[(i_start + 1):i_end])
                res = f(raw_res)
                # Replace negative sign in front of number by _ to avoid *- or +-
                if res < 0:
                    s_res = '_%s' % (-res)
                else:
                    s_res = str(res)
                # place the result into original expression
                new_s = '%s%s%s' % (s[:(i_start - f_len)], s_res, s[(i_end + 1):])
                return self.ev(new_s)

        for ar_n, ar_f in zip(self.arithm_names, self.arithm_funs):
            if ar_n in s:
                s = s.split(ar_n)
                v = list(map(self.ev, s))
                res = v[0]
                for x in v[1:]:
                    res = ar_f(res, x)
                return res


if __name__ == "__main__":
    """
    import sys,os
    append_path = os.path.abspath(sys.argv[0])[:-20]
    print("Append to PYTHONPATH: %s" % (append_path))
    sys.path.append(append_path)
    """
    # s = '1+8*(2*(-4-3*(2-5))+(45-3))'
    # s = 'floor((4+3)/3)'
    # s = '5+3*2'
    # s = '-3-4*(-5-10)'
    calc = Calculator({'x':3})
    s = '3*(x+6)'
    print(calc.ev(s))

