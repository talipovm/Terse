"""
This module contains the components for formatting the main table in HTML
"""

br = '<br />'

brn = '<br />\n'

def tag(s, t, intag=''):
    shifted = ''
    indent = '    '
    for line in str(s).split("\n"):
        shifted += indent+line+"\n"
    return "<%(tag)s %(intag)s>\n%(tagbody)s</%(tag)s>\n" % {'tag': t, 'intag': intag, 'tagbody': shifted}


def img(source,width='450'):
    return brn + "<img src='%s' width=%s\n"  % (source,str(width)) + brn

def color(s, col_type):
    from Top import Top
    tp = Top()
    return tag(s,"SPAN style='color:%s'" % (tp.settings.color[col_type]))
