from ReportGenerator.Geom import Geom
from ReportComponents.Plot import Plot
from ReportGenerator.Top_ReportGenerator import Top_ReportGenerator
from ReportComponents.WebFile import WebFile

import logging
log = logging.getLogger(__name__)

class SinglePoint(Top_ReportGenerator):
    def __init__(self,we,parsed):
        self.scf_progress = list()
        super().__init__(we,parsed)

    def prepare_for_report(self):
        sp = self.parsed

        self.scf_ok = (sp.last_value('P_scf_done' )== 'True')
        self.do_scf_progress = not self.scf_ok
        if self.do_scf_progress:
            v = sp.last_value('P_scf_progress')
            if v is not None and len(v )>0:
                if isinstance(v[0] ,list):
                    self.scf_progress = list(zip(*v))
                else:
                    self.scf_progress = v
        self.q_Mulliken = sp.last_value('P_charges_Mulliken')
        self.q_Lowdin = sp.last_value('P_charges_Lowdin')
        self.charges_available = self.q_Mulliken or self.q_Lowdin

    def scf_conv_plot_html(self):
        # save the convergence plot
        yval = self.scf_progress
        xlab = 'Iteration'
        ylab = 'SCF energy, Hartree'
        plt = Plot(fname='-sp-conv.png', xlab=xlab, ylab=ylab, legend=ylab, x=None, y=yval)
        if plt.nonempty:
            plt.save_plot()
            return self.img_tag(plt.web_path)
        else:
            return 'Not enough data to produce convergence plot'

    def charges(self, charges,name):
        col_min, col_max = -1.0, 1.0
        script_on = "; ".join([
            "x='%(a)s'",
            "DATA '%(p)s @x'",
            "label %%.%(precision)s[%(p)s]",
            "color atoms %(p)s 'rwb' absolute %(col_min)f %(col_max)f"
        ]) % {
            'a': " ".join(charges),
            'p': 'property_' + name,
            'precision': str(3),
            'col_min': col_min,
            'col_max': col_max
        }
        return script_on


    def save_geom(self):
        G = str(Geom(self.we,self.parsed))
        if not G:
            return
        return WebFile(fname='.xyz',content=G).write()

    def load_in_jmol(self, webpath):
        cmd = [
            self.we.jmol_load_file(webpath),
            self.we.jmol_text('Single point calculation, last geometry')
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
                'Single Point step: ',
                self.we.html_button(load_command, 'Energy') # and create button to load (useful for several step-jobs)
            ]
            [self.add_left(s) for s in out_html]
        else:
            self.add_left(self.color_tag('No coordinates found!','err'))

        if not self.scf_ok:
            self.add_right(self.color_tag('Incomplete SCF!','err'))
            self.add_right(self.br_tag)

        if self.do_scf_progress:
            self.add_right(self.scf_conv_plot_html())
            self.add_right(self.br_tag)

        if self.charges_available:
            if self.q_Mulliken:
                s  = self.we.html_button(self.charges(self.q_Mulliken,'Mulliken'), 'Mulliken')
                self.add_right(s)
            if self.q_Lowdin:
                s  = self.we.html_button(self.charges(self.q_Lowdin,'Lowdin'), 'Lowdin')
                self.add_right(s)
            button_off = self.we.html_button('label off;color atoms cpk', 'Off')
            self.add_right(button_off)
            self.add_right(self.br_tag)

        return self.get_cells()