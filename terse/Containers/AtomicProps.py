import logging
from Top import Top

log = logging.getLogger(__name__)

if __name__ == "__main__":
    import sys
    sys.path.append('..')


class AtomicProps(Top):
    """
    This is a container for atomic properties.
    Expected functionality:
        1. Provide data structure to store atomic properties,
        2. Visualize properties in Jmol using labels and color gradients
    """

    def __init__(self, attr='partialCharge', data=None):
        self.attrname = attr
        self.precision = 6
        if data is None:
            self.data = []
        else:
            setattr(self, attr, data)
            self.data = data

    def __str__(self):
        """
        Represents self.data as string with space-separated values
        :rtype: string
        """
        if len(self.data) == 0:
            return ''
        a0 = self.data[0]
        type2format = {
            int: '%i ',
            float: '%.' + str(self.precision) + 'f ',
            str: '%s '
        }
        template = (type2format[a0.__class__]) * len(self.data)
        s = template % tuple(self.data)
        return s.rstrip()

    def webdata(self):
        """
        Create a button on the web page that will color and label each atom
        """
        h_1 = ""
        h_2 = ""
        col_min = -1.0
        col_max = 1.0
        if '_H' in self.attrname:
            h_1 = "color atoms cpk; label off ; select not Hydrogen ;"
            h_2 = "; select all"
        elif '_proton' in self.attrname:
            # Sample options for showing 1H NMR chemical shifts
            h_1 = "color atoms cpk; label off ; select Hydrogen ;"
            h_2 = "; select all"
            col_min = 0.0
            col_max = 9.0
        elif '_carbon' in self.attrname:
            # Sample options for showing 13C NMR chemical shifts
            h_1 = "color atoms cpk; label off ; select Carbon ;"
            h_2 = "; select all"
            col_min = 0.0
            col_max = 200.0

        script_on = "x='%(a)s'; DATA '%(p)s @x'; %(h_1)s label %%.%(precision)s[%(p)s]; color atoms %(p)s 'rwb' absolute %(col_min)f %(col_max)f %(h_2)s" % {
            'a': str(self),
            'p': 'property_' + self.attrname,
            'precision': str(self.precision),
            'col_min': col_min,
            'col_max': col_max,
            'h_1': h_1,
            'h_2': h_2
        }
        we = self.settings.Engine3D()
        return we.html_button(script_on, self.attrname)


if __name__ == '__main__':
    from Settings import Settings
    from Top import Top
    Top.settings = Settings()

    ap = AtomicProps(attr='partialCharge')
    ap.data = [-0.2, -0.2, -0.2, 0.3, 0.3, .5, -.5]
    # print ap
    print(ap.webdata())
