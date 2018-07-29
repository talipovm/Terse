from ReportGenerator.Geom import Geom
from ReportComponents.Plot import Plot
from ReportGenerator.Top_ReportGenerator import Top_ReportGenerator
from ReportComponents.WebFile import WebFile
from ReportGenerator.Charges import Charges

import logging
log = logging.getLogger(__name__)

class Opt(Top_ReportGenerator):
    def __init__(self,we,parsed):
        super().__init__(we,parsed)
        self.multiple_geoms = False

    def prepare_for_report(self):
        self.opt_ok = (self.parsed.last_value('P_opt_ok')=='True')
        self.do_opt_progress = self.settings.FullGeomInfo or not self.opt_ok
        self.n_steps = self.parsed.last_value('P_opt_iter')
        self.measure_bonds = self.parsed.last_value('P_bond_constraints')

        if self.do_opt_progress:
            self.prepare_opt_convergence()

        if self.opt_ok:
            self.charges = Charges(self.we, self.parsed)
        else:
            self.charges = None

        if self.do_opt_progress:
            self.parsed_g = self.parsed.data[1:]  # TODO 1 might be program-dependent
        else:
            self.parsed_g = [self.parsed]

    def prepare_opt_convergence(self):
        conv = {'max_force':[],'rms_force':[],'max_displacement':[],'rms_displacement':[]}
        for cnv_type in conv.keys():
            s = 'P_'+cnv_type
            conv[cnv_type] = [o.last_value(s) for o in self.parsed.data[1:] if o.last_value(s) is not None]
        conv = {k:v for k,v in conv.items() if len(v) > 0}  # remove absent convergence criteria
        if len(conv)==0:
            self.do_opt_progress = False
            log.debug('Did not find any convergence criteria for plotting')
        else:
            (self.ylab, self.yval) = zip(*conv.items())  # reshape them

    def opt_conv_plot_html(self):
        plt = Plot(fname='-opt-conv.png', xlab='x', ylab='Convergence', legend=self.ylab, x=None, y=self.yval)
        if plt.nonempty:
            plt.save_plot()
            return self.img_tag(plt.web_path)
        else:
            return 'Not enough data to produce convergence plot'

    def opt_steps(self):
        return "Steps: %s" % self.n_steps

    def measurements(self):
        out = ['measure %s %s' % tuple(m) for m in self.measure_bonds]
        return "; ".join(out)

    def save_geom(self):
        v = [str(Geom(self.we,g)) for g in self.parsed_g]
        self.multiple_geoms = (len(v) > 1)
        s_geoms = "\n".join(v)
        if not s_geoms:
            return ''
        return WebFile(fname='-opt.xyz',content=s_geoms).write()

    def load_in_jmol(self, webpath):
        if self.do_opt_progress:
            label = 'Geometry optimization, step @{_modelNumber}'
        else:
            label = 'Optimized geometry'
        cmd = [
            self.we.jmol_load_file(webpath),
            'frame last',
            self.measurements(),
            self.we.jmol_text(label)
            ]
        return "; ".join(cmd)

    def jobtype_html(self):
        sx = self.strong_tag('OPT')
        if self.opt_ok:
            return sx
        else:
            return self.color_tag(sx, 'err')

    def report_text(self):
        if not self.opt_ok:
            self.add_right('Geometry optimization is incomplete!')

    def report_html(self):
        webpath = self.save_geom()
        if webpath:
            load_command = self.load_in_jmol(webpath)
            out_html = [
                self.we.jmol_command_to_html(load_command), # load immediately
                'Optimization step: ',
                self.we.html_button(load_command, 'Opt'), # and create button to load (useful for several step-jobs)
                self.br_tag
            ]
            [self.add_left(s) for s in out_html]

            if self.multiple_geoms:
                self.add_left(self.we.html_geom_play_controls())
                self.add_left(self.br_tag)
        else:
            self.add_left(self.color_tag('No coordinates found!','err'))

        self.add_right(self.jobtype_html())
        self.add_right(self.br_tag)

        self.add_right(self.opt_steps())
        self.add_right(self.br_tag)

        if not self.opt_ok:
            self.add_right(self.color_tag('Incomplete geometry optimization!','err'))
            self.add_right(self.br_tag)

        if self.do_opt_progress:
            self.add_right(self.opt_conv_plot_html())
            self.add_right(self.br_tag)

        if webpath and self.charges is not None:
            self.add_both(self.charges.button_bar(load_command))

        return self.get_cells()