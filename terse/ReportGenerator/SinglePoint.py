from ReportGenerator.Geom import Geom
from ReportComponents.Plot import Plot
from ReportGenerator.Top_ReportGenerator import Top_ReportGenerator
from ReportComponents.WebFile import WebFile
from ReportGenerator.Charges import Charges

import logging
log = logging.getLogger(__name__)

class SinglePoint(Top_ReportGenerator):
    def __init__(self,we,parsed):
        self.scf_progress = list()
        super().__init__(we,parsed)

    def prepare_for_report(self):
        sp = self.parsed

        scf_started = (sp.last_value('P_scf_started' )== 'True')
        scf_done = (sp.last_value('P_scf_done' )== 'True')
        self.scf_ok = (scf_started == scf_done)
        self.do_scf_progress = not self.scf_ok
        if self.do_scf_progress:
            v = sp.last_value('P_scf_progress')
            if v is not None and len(v )>0:
                if isinstance(v[0] ,list):
                    self.scf_progress = list(zip(*v))
                else:
                    self.scf_progress = v
        if self.scf_ok:
            self.charges = Charges(self.we,self.parsed)
        else:
            self.charges = None

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

    def jobtype_html(self):
        P = self.parsed
        jobtype = P.last_value('P_jobtype')
        if not jobtype:
            jobtype = P.last_value('P_unknown_jobtype')
            if jobtype is None:
                return 'Job type not determined'
        if isinstance(jobtype,list):
            sx = " ".join(jobtype).upper()
        else:
            sx = jobtype.upper()
        sx = self.strong_tag(sx)
        if P.last_value('P_term_ok')== 'True':
            return sx
        else:
            return self.color_tag(sx, 'err')

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

        self.add_right(self.jobtype_html())
        self.add_right(self.br_tag)

        if not self.scf_ok:
            self.add_right(self.color_tag('Incomplete SCF!','err'))
            self.add_right(self.br_tag)

        if self.do_scf_progress:
            self.add_right(self.scf_conv_plot_html())
            self.add_right(self.br_tag)

        if webpath and self.charges is not None:
            self.add_both(self.charges.button_bar(load_command))

        return self.get_cells()