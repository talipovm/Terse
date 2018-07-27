from ReportGenerator.Geom import Geom
from ReportGenerator.Top_ReportGenerator import Top_ReportGenerator
from ReportComponents.WebFile import WebFile
from ReportGenerator.Charges import Charges
from ReportComponents.Plot import Plot

import logging
log = logging.getLogger(__name__)

class IRC(Top_ReportGenerator):

    def __init__(self,we,parsed):
        super().__init__(we,parsed)

    def __init__(self,we,parsed):
        super().__init__(we,parsed)

    def prepare_for_report(self):
        self.n_steps = len(self.parsed.data) - 1
        self.prepare_irc_convergence()
        self.charges = Charges(self.we, self.parsed)
        self.plot_irc = True

    def prepare_irc_convergence(self):

        self.irc_x = [0] + [o.last_value('P_irc_coord') for o in self.parsed.data[1:]]
        self.irc_e = [o.last_value('P_scf_e') for o in self.parsed.data]

        if len(self.irc_x)!=len(self.irc_e):
            self.plot_irc = False
            log.error('Different lengths of irc_x and irc_e!')

    def opt_conv_plot_html(self):
        plt = Plot(fname='-irc.png', xlab='IRC coordinate', ylab='Energy', legend='IRC Plot', x=self.irc_x, y=self.irc_e)
        if plt.nonempty:
            plt.save_plot()
            return self.img_tag(plt.web_path)
        else:
            return 'Not enough data to produce convergence plot'

    def save_geom(self):
        v = [str(Geom(self.we,g)) for g in self.parsed.data]
        self.multiple_geoms = (len(v) > 1)
        s_geoms = "\n".join(v)
        if not s_geoms:
            return ''
        return WebFile(fname='-irc.xyz',content=s_geoms).write()

    def load_in_jmol(self, webpath):
        label = 'IRC, step @{_modelNumber}'
        cmd = [
            self.we.jmol_load_file(webpath),
            'frame last',
            self.we.jmol_text(label)
            ]
        return "; ".join(cmd)

    def report_text(self):
        pass

    def report_html(self):
        webpath = self.save_geom()
        if webpath:
            load_command = self.load_in_jmol(webpath)
            out_html = [
                self.we.jmol_command_to_html(load_command), # load immediately
                'IRC: ',
                self.we.html_button(load_command, 'IRC'), # and create button to load (useful for several step-jobs)
                self.br_tag
            ]
            [self.add_left(s) for s in out_html]

            if self.multiple_geoms:
                self.add_left(self.we.html_geom_play_controls())
                self.add_left(self.br_tag)
        else:
            self.add_left(self.color_tag('No coordinates found!','err'))

        self.add_right(self.strong_tag("IRC"))
        self.add_right(self.br_tag)

        if self.plot_irc:
            self.add_right(self.opt_conv_plot_html())
            self.add_right(self.br_tag)

        if webpath and self.charges is not None:
            self.add_both(self.charges.button_bar(load_command))

        return self.get_cells()