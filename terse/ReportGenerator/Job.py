import logging
log = logging.getLogger(__name__)

from ReportGenerator.Scan import Scan
from ReportGenerator.IRC import IRC
from ReportGenerator.DRC import DRC
from ReportGenerator.Freq import Freq
from ReportGenerator.Opt import Opt
from ReportGenerator.NoJobType import NoJobType
from ReportGenerator.SinglePoint import SinglePoint
from ReportGenerator.Top_ReportGenerator import Top_ReportGenerator

class Job(Top_ReportGenerator):

    def __init__(self, we,parsed):
        super().__init__(we,parsed)

    def prepare_for_report(self):
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

    def level_of_theory_html(self):
        method = self.parsed.last_value('P_wftype')
        basis = self.parsed.last_value('P_basis')
        lot = "%s / %s" % (method,basis)
        return self.color_tag(lot.upper(), 'lot')

    def fragmentation_html(self):
        P = self.parsed
        if P.last_value('P_wftype_fragment') is not None:
            lot2 = 'Fragmentation scheme: ' + P.last_value('P_wftype_fragment')
            return self.color_tag(lot2, 'lot')

    def symmetry_html(self):
        sym = self.parsed.last_value('P_sym')
        sym_axis = self.parsed.last_value('P_sym_axis')
        if sym_axis is not None:
            return "Symmetry: %s, N=%s\n" % (sym,sym_axis)
        else:
            return "Symmetry: %s\n" % sym

    def charge_mult_html(self):
        charge = "Charge: %s; " % self.parsed.last_value('P_charge')
        mult = "Mult: %s\n" % self.parsed.last_value('P_mult')
        return charge + mult

    def open_shell_html(self):
        if self.parsed.last_value('P_open_shell')== 'True':
            return "Open Shell; S2= %s,\n" % self.parsed.last_value('P_S2')

    def scf_energy_html(self):
        try:
            return "Last Total Energy= %-11.6f\n" % float(self.parsed.last_value('P_scf_e'))
        except TypeError:
            return "Total Energy %s\n" % self.color_tag('N/A','err')

    def scf_failed_html(self):
        if self.parsed.last_value('P_scf_notconv')== 'True':
            return self.color_tag('SCF did not converge!', 'err')

    def solvent_html(self):
        P = self.parsed
        if P.last_value('P_solvent') is not None:
            sx = 'Solvation: '
            if P.last_value('P_solv_model') is not None:
                sx += '%s (%s)' % (P.last_value('P_solv_model'), P.last_value('P_solvent'))
            return self.color_tag(sx, 'lot')

    def coupled_cluster_html(self):
        if self.parsed.last_value('P_ccsd_pTp_energy') is not None:
            return "Last CCSD(T) Energy= %-11.6f\n" % float(self.parsed.last_value('P_ccsd_pTp_energy'))

    def t1_diagnostics_html(self):
        if self.parsed.last_value('P_T1_diagnostic') is not None:
            T1 = float(self.parsed.last_value('P_T1_diagnostic'))
            s_T1 = "T1 diagnostic= %.3f\n" % T1
            if T1 >= 0.025:
                s_T1 = self.color_tag(s_T1, 'err')
            return s_T1

    def report_text(self):
        pass

    def report_html(self):
        self.add_left(self.we.initiate_jmol_applet()) # initialize an JSMol applet
        out_html = [
            #self.jobtype_html(),
            self.level_of_theory_html(),
            self.solvent_html(),
            self.fragmentation_html(),
            self.symmetry_html(),
            self.charge_mult_html(),
            self.open_shell_html(),
            self.scf_energy_html(),
            self.scf_failed_html(),
            self.coupled_cluster_html(),
            self.t1_diagnostics_html()
        ]
        [self.add_right(s + self.br_tag) for s in out_html if s]

        P = self.parsed
        jobtype = P.last_value('P_jobtype')

        if jobtype is None:
            self.add_both(NoJobType(self.we, P).report())
            return self.get_cells()

        job_type_found = False
        job_types = {'scan':Scan,'irc':IRC,'opt':Opt,'drc':DRC}
        for name,Gen in job_types.items():
            if name not in jobtype:
                continue
            P = P.separate(name)
            self.add_both(Gen(self.we, P).report())
            job_type_found = True
            break
        if 'freq' in jobtype:
            if 'opt' in jobtype and P.last_value('P_opt_ok') != 'True':
                self.add_both(Freq(self.we, P.data[-1]).report())
            else:
                self.add_both(Freq(self.we, P).report())
            return self.get_cells()

        if not job_type_found:
            self.add_both(SinglePoint(self.we, P).report())

        return self.get_cells()