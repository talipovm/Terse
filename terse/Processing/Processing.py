import re
from Top import Top
from Tools.misc import strip_all,unquote_if_quoted
import pickle

import logging
log = logging.getLogger(__name__)

class Processing(Top):

    def __init__(self, PI=None, parsed=None):
        super().__init__()
        self.PI = PI
        self.parsed = parsed

    def command_group(self, s, before):
        """
        Example:
        separator(new_step) -> opt
        Object is changed internally
        :param s:
        :return:
        """
        if before:
            s_re = re.search(r'aggregate_before\((.*)\)\s*->\s*(.*)', s)
        else:
            s_re = re.search(r'aggregate_after\((.*)\)\s*->\s*(.*)', s)
        if s_re is None:
            raise SyntaxError
        separator_key, new_key = s_re.groups()
        self.parsed.group_container_by_key(separator_key, new_key, before)

    def command_last(self, s):
        """
        :param s:
        :return:
        """
        s_re = re.search(r'last_value\((.*)\)\s*->\s*(.*)', s)
        if s_re is None:
            raise SyntaxError
        old_key, new_key = s_re.groups()
        self.parsed.add_latest_rec(old_key=old_key, new_key=new_key)

    def command_nonempty(self, s):
        """
        :param s:
        :return:
        """
        s_re = re.search(r'nonempty\((.*)\)\s*->\s*(\S.*\S)\s*', s)
        if s_re is None:
            raise SyntaxError
        old_key, new_key = s_re.groups()
        self.parsed.edit_nonempty_rec(old_key=old_key, new_key=new_key)

    def command_joinunique(self, s):
        """
        :param s:
        :return:
        """
        s_re = re.search(r'join_unique\((.*)\)\s*->\s*(\S.*\S)\s*', s)
        if s_re is None:
            raise SyntaxError
        old_key, new_key = s_re.groups()
        self.parsed.join_unique(old_key=old_key, new_key=new_key)

    def command_assign(self, s):
        """
        :param s:
        :return:
        """
        s_re = re.search(r'\s*(\S.*\S)\s*->\s*(\S.*\S)\s*', s)
        if s_re is None:
            raise SyntaxError

        old_key, new_key = s_re.groups()
        old_value = new_value = None

        if '=' in old_key:
            old_key, old_value = strip_all(old_key.split('='))
            old_value = unquote_if_quoted(old_value)
        if '=' in new_key:
            new_key, new_value = strip_all(new_key.split('='))
            new_value = unquote_if_quoted(new_value)
        self.parsed.conditionally_add(old_key=old_key, new_key=new_key, old_value=old_value, new_value=new_value)

    def process_command(self, s):
        """
        :param s:
        :return:
        """
        if not s:
            return

        if s.find('aggregate_before')==0:
            self.command_group(s, before=True)
            return

        if s.find('aggregate_after')==0:
            self.command_group(s, before=False)
            return

        if s.find('last_value')==0:
            self.command_last(s)
            return

        if s.find('nonempty')==0:
            self.command_nonempty(s)
            return

        if s.find('join_unique')==0:
            self.command_joinunique(s)
            return

        if s.find('geom_use')==0:
            self.command_joinunique(s)
            return

        if '->' in s: # has to be the last_value one
            self.command_assign(s)
            return

    def postprocess(self):
        """
        :return:
        """
        for s_full in self.PI:
            s_nocomment = s_full.split('#')[0].rstrip()
            self.process_command(s_nocomment)
        return

if __name__ == "__main__":
    import sys

    sys.path.append('..')
    from Settings import Settings
    Top.settings = Settings()
    Top.settings.detailed_print = True

    from Tools.file2 import file2
    PI = file2('../../parsing-rules/gamess_processing.txt')

    G_parsed = pickle.load( open('G.p', 'rb') )

    P = Processing(PI=PI, parsed=G_parsed)
    P.postprocess()
    print(P)

