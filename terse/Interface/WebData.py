from Top import Top

import logging
log = logging.getLogger(__name__)
from Interface.XYZ import XYZ
from Geometry.Geom import Geom
import Tools.web as web
import Tools.misc as misc
from Tools.plot import Plot
if __name__ == "__main__":
    import sys
    sys.path.append('..')


class WebData(Top):

    def __init__(self, processed):
        self.processed = processed # is expected to be Processing().parsed
        super().__init__()

    def webdata_scan(self, scan):
        return

    def webdata_irc(self, irc):
        return

    def webdata_opt(self, opt):
        b1=b2=''
        opt_ok = opt.last_value('opt_ok')
        geoms = []
        if self.settings.FullGeomInfo or opt_ok!='True':
            # prepare geoms for web
            for opt_step in opt.data[1:]:
                G = Geom() # the only reason we use Geom() is that because it is compatible with XYZ().write
                G.prepare_for_web(geom=opt_step.last_value('geom'), bohr_units=(opt_step.last_value('geom_bohr') != 'empty'))
                geoms.append(G)

            # prepare convergence criteria
            convergence = {'max_force':[],'rms_force':[],'max_displacement':[],'rms_displacement':[]}
            for cnv_type in convergence.keys():
                convergence[cnv_type] = \
                    [opt_step.last_value(cnv_type) for opt_step in opt.data[1:] if opt_step.last_value(cnv_type) is not None]

            # save the convergence plot
            convergence = {k: v for k, v in convergence.items() if len(v) > 0}  # remove absent convergence criteria
            if len(convergence)>0:
                (ylab, yval) = zip(*convergence.items())  # reshape them
                plt = Plot(fname='-opt-conv.png', xlab='x', ylab='Convergence', legend=ylab, x=None, y=yval)
                plt.save_plot()
                b2 += web.img(plt.web_path)

            # Will show on top of the structure
            labeltext = 'Geometry optimization, step @{_modelNumber}'
        else:
            G = Geom()
            G.prepare_for_web(geom=opt.last_value('geom'), bohr_units=(opt.last_value('geom_bohr') != 'empty'))
            geoms.append(G)
            labeltext = 'Optimized geometry'
        # save geoms into XYZ and produce a path to it
        webpath = XYZ().write(fname='.xyz',geoms=geoms,vectors=False)

        # produce HTML code
        load_command  = self.we.jmol_load_file(webpath)
        load_command += '; ' + 'frame last'
        load_command += '; ' + self.we.jmol_text(labeltext)
        b1 += self.we.jmol_command_to_html(load_command)

        b1 += 'Optimization step: '
        b1 += self.we.html_button(load_command,'Opt') + web.brn

        # add a button bar to play geoms if more than one is given
        if len(geoms)>1:
            b1 += web.brn + self.we.html_geom_play_controls()
        return (b1,b2)

    def webdata_freq(self, freq):
        b1=b2=''

        P = freq.data[-1]

        G = Geom()
        G.prepare_for_web(geom=P.last_value('geom'), bohr_units=(P.last_value('geom_bohr') != 'empty'))

        # Reformat frequencies; TODO do it in processing
        vibs = []
        if P.get_value('vibrations') is not None:
            for vs in P.get_value('vibrations'):
                for v in zip(*vs):
                    vibs.append(misc.split(v, 3))

        im_freq = False
        if P.last_value('freqs') is not None:
            # TODO move to processing
            freqs_cm = [float(fr[0]) for fr in P.last_value('freqs')]

            b2 += web.br + "Freqs: "

            start_from_freq = 6 # TODO should not be hard-coded; some programs ignore TRANSL/ROT freqs automatically
            i = start_from_freq
            while freqs_cm[i] < 0:
                s_freq = "%.1f," % freqs_cm[i]
                if i == start_from_freq:
                    b2 += web.color(s_freq,'imag')
                    im_freq = True
                else:
                    b2 += web.color(s_freq,'err')
                i += 1
            b2 += "%.1f .. %.1f\n" % (freqs_cm[i], freqs_cm[-1])

        if im_freq:
            V = Geom()
            V.prepare_for_web(geom=vibs[start_from_freq])
            webpath = XYZ().write(fname='-freq.xyz',geoms=[G],vectors=V)
        else:
            webpath = XYZ().write(fname='-freq.xyz',geoms=[G])

        load_command  = self.we.jmol_load_file(webpath)
        load_command += '; ' + self.we.jmol_text('Vibrational analysis')
        b1 += self.we.jmol_command_to_html(load_command)

        # add a button bar to play vibration
        b1 += 'Frequency step: '
        b1 += self.we.html_button(load_command,'Freq')

        if im_freq:
            b2 += web.brn + web.color('Imaginary Freq(s) found!','imag')
            b1 += self.we.html_vibration_switch() + web.brn

        T = freq.get_value('thermo_temp')
        E_corr = freq.get_value('thermo_e_corr')
        H_corr = freq.get_value('thermo_h_corr')
        G_corr = freq.get_value('thermo_g_corr')
        thermo_units = freq.last_value('thermo_units')
        if E_corr:
            b2 += web.br + web.tag("Thermochemical corrections:","strong")
            for v in zip(*[T,E_corr,H_corr,G_corr]):
                b2 += web.br + "T=%s: E= %s, H= %s, G= %s " % v
                b2 += "(%s)\n" % thermo_units

        return (b1,b2)

    def webdata_sp(self, sp):
        b1=b2=''

        geoms = []
        G = Geom()
        G.prepare_for_web(geom=sp.last_value('geom'), bohr_units=(sp.last_value('is_geom_bohr') == 'True'))
        geoms.append(G)

        # save geoms into XYZ and produce a path to it
        webpath = XYZ().write(fname='.xyz',geoms=geoms,vectors=False)

        # produce HTML code
        load_command  = self.we.jmol_load_file(webpath)
        load_command += '; ' + self.we.jmol_text('Single point calculation, last_value geometry')
        b1 += self.we.jmol_command_to_html(load_command)

        b1 += 'Single Point step: '
        b1 += self.we.html_button(load_command,'Energy') + web.brn

        if sp.last_value('scf_notconv')== 'True' or sp.last_value('term_ok')!= 'True':

            # save the convergence plot
            scf_progress = sp.last_value('scf_progress')
            if scf_progress is not None and len(scf_progress)>0:
                if isinstance(scf_progress[0],list):
                    scf_progress = [i[0] for i in scf_progress]
            xlab = 'Iteration'
            ylab = 'SCF energy, Hartree'
            yval = scf_progress
            plt = Plot(fname='-sp-conv.png', xlab=xlab, ylab=ylab, legend=ylab, x=None, y=yval)
            if plt.nonempty:
                plt.save_plot()
                b2 += web.img(plt.web_path)
            else:
                b2 +=  web.br + 'Not enough data to produce convergence plot'

        return (b1,b2)

    def webdata_job(self, job):
        self.we = self.settings.Engine3D()
        #from Engine3D.JSMol import JSMol
        #self.we = JSMol()

        b1 = self.we.initiate_jmol_applet() # initialize an JSMol applet
        b2 = ''

        P = self.processed
        jobtype = P.last_value('final_jobtype')

        # jobtype
        if not jobtype:
            b2 +='Job type not determined'
            return (b1,b2)
        if isinstance(jobtype,list):
            sx = " ".join(jobtype).upper()
        else:
            sx = jobtype.upper()
        sx = web.br + web.tag(sx,'strong')
        if P.last_value('term_ok')== 'True':
            b2 += sx
        else:
            b2 += web.color(sx,'err')

        # level of theory
        lot = '%s/%s' % (P.last_value('wftype'), P.last_value('basis'))
        b2 += web.br + web.color(lot.upper(),'lot')

        # level of theory, additional record
        if P.last_value('wftype_fragment') is not None:
            lot2 = 'Fragmentation scheme: ' + P.last_value('wftype_fragment')
            b2 += web.br + web.color(lot2,'lot')

        # symmetry, charge, multiplicity
        b2 += web.br + "Symmetry: %s\n" % P.last_value('final_sym')
        b2 += web.br + "Charge: %s; "  % P.last_value('final_charge')
        b2 += "Mult: %s\n"  % P.last_value('final_mult')

        # open shell, s2
        if P.last_value('open_shell')== 'True':
                b2 += web.br + "Open Shell; S2= %s,\n" % P.last_value('S2')

        # last_value SCF energy
        try:
            b2 += web.br + "Last SCF Energy= %-11.6f\n" % float(P.last_value('scf_e'))
        except TypeError:
            b2 += web.br + "Last SCF Energy N/A\n"

        if P.last_value('scf_notconv')== 'True':
            b2 += web.br + web.color('SCF did not converge!','err')

        if P.last_value('final_solvent') is not None:
            sx = 'Solvation: '
            if P.last_value('final_solv_model') is not None:
                sx += '%s(%s)' % (P.last_value('final_solv_model'), P.last_value('final_solvent'))
            b2 += web.br + web.tag(sx,'lot')

        if P.last_value('ccsd_pTp_energy') is not None:
            b2 += web.br + "Last CCSD(T) Energy= %-11.6f\n" % float(P.last_value('ccsd_pTp_energy'))
            if P.last_value('T1_diagnostic') is not None:
                T1 = float(P.last_value('T1_diagnostic'))
                s_T1 = "T1 diagnostic= %.3f\n" % T1
                if T1 >= 0.025:
                    s_T1 = web.tag(s_T1,'err')
                b2 += web.br + s_T1
        # P is wrapped in the aggregation order: job > scan > irc > opt;
        # should unwrap in the same order:
        if 'scan' in jobtype:
            (s_b1,s_b2) = self.webdata_scan(P)
            b1 += s_b1
            b2 += s_b2
        else:
            P = P.data[0]

        if 'irc' in jobtype:
            (s_b1, s_b2) = self.webdata_irc(P)
            b1 += s_b1
            b2 += s_b2
        else:
            P = P.data[0]

        if 'opt' in jobtype:
            (s_b1, s_b2) = self.webdata_opt(P)
            b1 += s_b1
            b2 += s_b2
        else:
            P = P.data[0]

        if 'freq' in jobtype:
            (s_b1, s_b2) = self.webdata_freq(P)
            b1 += s_b1
            b2 += s_b2

        if 'sp' in jobtype:
            (s_b1, s_b2) = self.webdata_sp(P)
            b1 += s_b1
            b2 += s_b2
        return (b1,b2)

    def produce_html_code(self):
        if self.processed.aggregate_name == 'job':
            # multi-job file
            b1 = b2 = ''
            for job in self.processed:
                (s_b1, s_b2) = self.webdata_job(job)
                b1 += s_b1
                b2 += s_b2
            return (b1, b2)
        else:
            # single-job file
            return self.webdata_job(self.processed)
