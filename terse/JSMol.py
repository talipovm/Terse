import Tools.HTML
from Top import Top
import logging

log = logging.getLogger(__name__)

"""
jmol commands need to be wrapped into Jmol.script(ID, "...commands...")
Sometimes, it is preferable to do it immediately or within .webdata() function.
Accordingly, html_* elements represent controls that are ready to be inserted
into the web page, while jmol_* need to be wrapped up using jmol_command_to_html.

ID is defined based on self.settings.counter
"""
class JSMol(Top):

    def initiate_jmol_applet(self):
        s = "jmolApplet%s = Jmol.getApplet(\"jmolApplet%s\", Info)" % ((self.settings.counter,) * 2)
        return Tools.HTML.tag(s, 'SCRIPT')

    def jmol_command_to_html(self, s, intag=''):
        s2 = "Jmol.script(jmolApplet%(counter)s, \"%(script)s\" );" % {
            'counter': self.settings.counter,
            'script': s.replace('"', '\\"').replace("'", "\\'")  # s.replace('"',' &quot ')
        }
        return Tools.HTML.tag(s2, 'SCRIPT', intag=intag)


    def jmol_load_file(self, webpath):
        s = 'load %s' % webpath
        return s + '; ' + self.settings.JavaOptions

    def html_load_file(self, *args):
        s = self.jmol_load_file(*args)
        return self.jmol_command_to_html(s)


    def jmol_isosurface(self, webpath='', isovalue='', surftype='', webpath_other='', name='', colors='',
                        use_quotes=False):
        isovals = {
            'potential': '0.001',
            'spin': '0.001',
            'spin2': '0.001',
            'mo': '0.03',
            'amo': '0.03',
            'bmo': '0.03'
        }
        surftypes = {
            'potential': 'isosurface %s cutoff %s %s color absolute -0.03 0.03 map %s',
            'spin': 'isosurface %s sign cutoff  %s %s %s',
            'spin2': 'isosurface %s cutoff %s %s %s',
            'mo': 'isosurface %s phase cutoff %s %s %s',
            'amo': 'isosurface %s phase cutoff %s %s %s',
            'bmo': 'isosurface %s phase cutoff %s %s %s'
        }
        coltypes = {
            'mo': 'phase %s %s opaque' % (self.settings.color_mo_plus, self.settings.color_mo_minus),
            'amo': 'phase %s %s opaque' % (self.settings.color_mo_plus, self.settings.color_mo_minus),
            'bmo': 'phase %s %s opaque' % (self.settings.color_mo_plus, self.settings.color_mo_minus),
            'spin': 'red blue',
            'spin2': 'blue'
        }

        st_lower = surftype.lower().split('=')[0]
        if st_lower in surftypes:
            st = surftypes[st_lower]
        else:
            st = 'isosurface %s cutoff %s %s %s'

        if not isovalue:
            if st_lower in isovals:
                isovalue = isovals[st_lower]
            else:
                isovalue = '0.03'

        color = colors
        if (st_lower in coltypes) and (not color):
            color = coltypes[st_lower]
        if not color:
            color = 'translucent'

        if use_quotes:
            webpath = '"%s"' % (webpath)
            if webpath_other:
                webpath_other = '"%s"' % (webpath_other)

        log.debug('Plotting isosurface; surftype: %s' % (st_lower))
        st2 = st % (name, isovalue, webpath, webpath_other) + '; color isosurface %s' % (color)
        log.debug(st2)
        return st2

    def html_isosurface(self, *args):
        s = self.jmol_isosurface(*args)
        return self.jmol_command_to_html(s)


    def jmol_jvxl(self, webpath='', name='', use_quotes=False):
        if use_quotes:
            webpath = '"%s"' % (webpath)
        return 'isosurface %s %s' % (name, webpath)

    def html_jvxl(self, *args):
        s = self.jmol_jvxl(*args)
        return self.jmol_command_to_html(s)


    def jmol_cli(self):
        return 'jmolCommandInput("Execute")'

    def html_cli(self):
        s = self.jmol_cli()
        return self.jmol_command_to_html(s)


    def jmol_text(self, label, position='top left', color='green'):
        return "set echo %s; color echo %s; echo %s;" % (position, color, label)

    def html_text(self, *args,**kwargs):
        s = self.jmol_text(*args,**kwargs)
        return self.jmol_command_to_html(s)


    def html_button(self, action, label):
        return '<button type="button" onclick="javascript:Jmol.script(jmolApplet%(count)s, \'%(action)s\')">%(label)s</button>\n' % {
            'count': self.settings.counter,
            'action': action.replace('"', '\\"').replace("'", "\\'"),  # s.replace('"',' &quot '),
            'label': label,
        }

    def html_checkbox(self, on, off, label=''):
        s2 = "Jmol.jmolCheckbox(jmolApplet%(counter)s, \"%(script_on)s\", \"%(script_off)s\", \"%(label)s\" );" % {
            'counter': self.settings.counter,
            'script_on': on,
            'script_off': off,
            'label': label
        }
        return Tools.HTML.tag(s2, 'SCRIPT')

    def jmol_radiogroup(self, options):
        s = ''
        for opt in options:
            s2 = ''
            for o in opt:
                s2 += '"%s", ' % (o)
            s += '[%s],' % (s2[:-2])
        return 'jmolRadioGroup([%s])' % s[:-1]

    # TODO I suspect that it is currently broken but never tried it
    def html_radiogroup(self, *args):
        s = self.jmol_radiogroup(*args)
        return self.jmol_command_to_html(s)

    def jmol_menu(self, options):
        s = ''
        for opt in options:
            s2 = ''
            for o in opt: s2 += '"%s", ' % (o)
            s += '[%s],' % (s2[:-2])
        return 'jmolMenu([%s])' % s[:-1]

    # TODO I suspect that it is currently broken but never tried it
    def html_menu(self, *args):
        s = self.jmol_menu(*args)
        return self.jmol_command_to_html(s)


    def html_geom_play_controls(self):
        ButtonFirst = self.html_button('frame 1', '<<')
        ButtonPrev = self.html_button('anim direction +1 ; frame prev', '<')
        ButtonNext = self.html_button('anim direction +1 ; frame next', '>')
        ButtonLast = self.html_button('frame last', '>>')
        ButtonPlayOnce = self.html_button('anim mode once; frame 1; anim direction +1 ; anim on', 'Play once')
        ButtonPlayBack = self.html_button('anim mode once; frame 1; anim direction -1 ; anim on', 'Play back')
        ButtonStop = self.html_button('anim off', 'Stop')
        return ButtonFirst + ButtonPrev + ButtonNext + ButtonLast + ButtonPlayOnce + ButtonPlayBack + ButtonStop

        """
        opts = []
        for a in (1,5,10,25,50):
            opts.append(['set animationFPS %s' % (a), a])
        opts[2].append('checked')

        s += self.JMolMenu(opts,script=False)
        """


    def html_vibration_switch(self):
        return self.html_checkbox("vibration on", "vibration off", "Vibration")

    def jmol_measurements(self, ss):
        toJmol = ''
        for s in ss:
            left, right = s.find('('), s.find(')')
            if left and right and (right > left):
                toJmol += '; measure %s; ' % (s[left + 1:right].replace(',', ' '))
        return toJmol

    def html_measurements(self, *args):
        s = self.jmol_measurements(*args)
        return self.jmol_command_to_html(s)


    # OLD METHODS, TODO EVENTUALLY TO BE REVISED
    def JSMolStyle(self, s):
        s2 = "Jmol.script(jmolApplet%(counter)s, \"%(script)s\" );" % {
            'counter': self.settings.counter,
            'script': s.replace('"', '\\"').replace("'", "\\'")  # s.replace('"',' &quot ')
        }
        return s2

    def JSMolScript(self, s, intag=''):
        s2 = self.JSMolStyle(s)
        return Tools.HTML.tag(s2, 'SCRIPT', intag=intag)

    def JMolApplet(self, webpath='', ExtraScript=''):
        s = "jmolApplet%s = Jmol.getApplet(\"jmolApplet%s\", Info)" % ((self.settings.counter,) * 2)
        script = self.JMolLoad(webpath=webpath, ExtraScript=ExtraScript)
        s += ';\n' + self.JSMolStyle(script)
        return Tools.HTML.tag(s, 'SCRIPT')

    def JMolLoad(self, webpath='', ExtraScript=''):
        sl = ''
        if webpath:
            sl = 'load %s' % (webpath)
            # sl = 'load %s;%s' % (webpath, self.settings.JavaOptions)
        if ExtraScript:
            sl += ExtraScript
        return sl

if __name__ == "__main__":
    import sys

    sys.path.append('..')
    # from Settings import Settings
