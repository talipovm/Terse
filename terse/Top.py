import logging

log = logging.getLogger(__name__)


class Top:
    def __init__(self):
        self.top = True
        pass

    def __str__(self, depth=0, full=False):
        """
        Returns a string representation of the class
        :param depth: indentation for recursive class print outs
        :param full: full or brief information to be printed
        :rtype: string
        """
        try:
            full = self.settings.detailed_print
        except:
            full = False

        # for the indentation purposes
        shift = '    ' * depth
        shift_p1 = shift + '    '

        s = '%s\n' % self.__class__

        for a, v in sorted(self.__dict__.items()):

            if hasattr(v, 'top'):
                # If another class object is attached, then recursively call __str__ with increased offset
                if full:
                    vstr = v.__str__(depth + 1)
                else:
                    vstr = shift_p1 + v.__repr__()

            elif isinstance(v, (list, tuple)):
                # convert lists/tuples to strings
                if full:
                    if hasattr(v[0], 'top'):  # List of Top class instances?
                        vstr = '['
                        for v2 in v:
                            vstr += v2.__str__(depth + 1) + ('\n' + shift_p1) * 2 + ','
                        vstr += ']'
                    else:
                        vstr = str(v)
                else:
                    vstr = '%i elements of %s' % (len(v), v[0].__class__)
            else:
                # simple value?
                try:
                    vstr = str(v)
                except:
                    vstr = '...'

            s += shift + '%s = ' % a
            s += vstr + '\n'
        return s[:-1]

    def __iter__(self):
        """
         Returns attribute/value pairs, one at a time, sorted by keys
        :return: attr, value
        """
        for attr, value in sorted(self.__dict__.items()):
            yield attr, value

    def parse(self, *args):
        log.error('Requested parser has not been implemented yet for this format')

    def usage(self, *args):
        log.error('No CPU statistics can be collected for this format')

    def postprocess(self):
        pass

    def webdata(self, *args):
        log.error('Web output has not been implemented yet for this format')
        return '', ''

    def write(self, *args):
        log.error('Saving file has not been implemented yet for this format')
        return '', ''


if __name__ == "__main__":
    from Settings import Settings

    top = Top()
    top.settings = Settings()
    top.settings.detailed_print = False
    top.x = (Settings(), Settings())
    top.a = [1, 2, 3]
    print(top)
