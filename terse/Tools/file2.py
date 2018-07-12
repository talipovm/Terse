import io
import logging
import os
import re

log = logging.getLogger(__name__)


class file2(io.TextIOWrapper):
    """
    Provides tools useful for navigating through and finding data
    in the output files
    """

    def __init__(self, name, mode='r', *args, **kwargs):
        # super().__init__(*args, **kwargs)
        self.s = ''
        self.lnum = 0
        self.ssplit = []
        self.sstrip = ''
        self.fname = name
        try:
            self.f = open(name, mode)
            log.debug('%s was opened for reading' % name)
        except FileNotFoundError:
            log.error('Cannot open %s for reading' % name)

    def __iter__(self):
        return self

    def __next__(self):
        """
        Read the next line.
        Return a string and update self.s
        """
        self.s = next(self.f)  # it will raise StopIteration at EOF
        #self.lnum += 1

        return self.s

    def skip_n(self, n=1):
        """
        Skip the next (n-1) lines and store the n-th line as self.s
        If n = 0, do nothing
        """
        for _ in range(n):
            next(self)

    def skip_until(self, pattern, offset=0, regexp=False):
        """
        Skip the file lines until a pattern is found.
        Pattern might be a single substring or a list of them.
        If pattern is a list, then a value returned is an index of the matching string
        If pattern is an empty string or list or tuple, will skip_n until the line
        that is empty or contains only white spaces.
        The first matching (and offset) line will be stored as self.s
        The search will be started from the current line.

        :param pattern: Pattern to search
        :param offset: Int; how many lines to skip_n after the pattern is found.
        :param regexp: Boolean; treat patterns as regexps.
        """
        instance_hit = None
        # next(self)
        if pattern:
            if not isinstance(pattern, (list, tuple)):
                ps = [pattern, ]
            else:
                ps = pattern
            while instance_hit is None:
                for i in range(len(ps)):
                    if regexp:
                        hit = re.search(ps[i], self.s)
                    else:
                        hit = (ps[i] in self.s)
                    if hit:
                        instance_hit = i
                        break
                else:  # not found
                    next(self)
        else:
            # pattern is an empty string
            while self.s.strip() != '':
                next(self)
        self.skip_n(offset)

        return instance_hit

    def nstrip(self):
        """
        Read and strip the next line
        Return a string and update self.sstrip
        """
        self.sstrip = next(self).strip()
        return self.sstrip

    def nrstrip(self):
        """
        Read and right strip the next line
        Return a string and update self.sstrip
        """
        self.sstrip = next(self).rstrip()
        return self.sstrip

    def nsplit(self):
        """
        Read, strip, ans split by white spaces the next line
        Return a string and update self.sstrip and self.ssplit
        """
        self.ssplit = self.nstrip().split()
        return self.ssplit

    def find_text_block(self, start_match='', start_offset=0, end_match='', end_offset=-1):
        """
        reads a textblock from the file
        #
        #
        #  Say, start_offset = 3, and end_offset = -1:
        #   start_match : 0 : -
        #   Junk        : 1 : -
        #   Junk        : 2 : -
        #   Info        : 3 : +
        #   Info        :   : +
        #   Info        :-1 : +
        #   end_match   : 0 : -
        #   Other       : 1 : -
        #   Other       : 2 : -
        #
        #  In this case, only strings marked by '+' sign will be extracted
        #  If start_match is not defined, block will start at current position+start_offset
        #  If end_match is not defined, block will end at an empty string
        """
        # Positioning
        if start_match:
            self.skip_until(start_match)

        self.skip_n(start_offset)

        # Define criteria for stop
        def find_second_match(match, s):
            # noinspection PyRedundantParentheses
            if (match) and (match in s): return True
            if (match == '') and (s.strip() == ''): return True
            return False

        # Fill array
        ss = [self.s.strip(), ]
        while not find_second_match(end_match, self.s):
            ss.append(self.nstrip())
        if end_offset < 1:
            ss = ss[0:(len(ss) + end_offset)]
        else:
            # Add lines after the stop match
            for i in range(end_offset):
                ss.append(self.nstrip())

        return ss

    def close(self):
        self.f.close()


if __name__ == "__main__":
    DebugLevel = logging.DEBUG
    logging.basicConfig(level=DebugLevel)

    fname = "test-test2.txt"
    text_file = open(fname, "w")
    text_file.write("""
    X
    Info0
    X
    Top1
    ---
    Info1
    Info2
    ---
    Top2
    Info3
    """)
    text_file.close()

    f = file2(fname)
    print(f.find_text_block('Top1', 2, 'Top2', 1))
    f.close()

    os.remove(fname)
