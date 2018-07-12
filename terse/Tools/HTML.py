from Top import Top
import logging
log = logging.getLogger(__name__)

class HTML(Top):
    def __init__(self):
        self.s = ''
        self.tableBody = ''

    def __str__(self):
        return self.s

    def readTemplate(self,fname=''):
        if not fname:
            fname = '%s/data/terse-%s.html' % (self.settings.selfPath,self.settings.Engine3D.__name__)
        self.s = open(fname).read()

    def addTableRow(self,*args):
        row = ''
        for a in args:
            row += tag(a, 'td') + '\n'
        self.tableBody += tag(row, 'tr')

    def write(self, file=''):
        if not file:
            file = self.settings.OutputFolder + '/' + self.settings.tersehtml
        try:
            f = open(file,'w')
        except IOError:
            log.critical('Cannot open %s for writing' % (file))
            return
        f.write(self.insert_HTML_fields())
        f.close()
        log.debug('Web page %s was updated' % (file))

    def insert_HTML_fields(self):
        d = {
                'JSMolPath' : self.settings.JSMolLocation,
                'timestamp' : self.settings.timestamp,
                'JMolPath'  : self.settings.JmolPath,
                'TableBody' : self.tableBody,
                'JMolWinX'  : self.settings.JmolWinX,
                'JMolWinY'  : self.settings.JmolWinY,
                'jmoloptions'  : self.settings.JavaOptions,
            }
        return self.s % d


def tag(s, t, intag=''):
    shifted = ''
    indent = '    '
    for line in str(s).split("\n"):
        shifted += indent+line+"\n"
    return "<%(tag)s %(intag)s>\n%(tagbody)s</%(tag)s>\n" % {'tag': t, 'intag': intag, 'tagbody': shifted}


if __name__ == "__main__":
    h = HTML()
    from Settings import Settings
    h.settings = Settings()
    tr = tag('abcd', 'tr')

    # This code is outdated!
    h.makeHeader()
    h.makeLine('abc','def')
    h.makeTail()
    print(h)
br = '<br />'
brn = '<br />\n'


def img(source,width='450'):
    return brn + "<img src='%s' width=%s\n"  % (source,str(width)) + brn


def color(s, col_type):
    from Top import Top
    tp = Top()
    return tag(s,"SPAN style='color:%s'" % (tp.settings.color[col_type]))