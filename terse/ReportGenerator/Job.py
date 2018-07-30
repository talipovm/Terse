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
import re

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
        if method is None:
            method = 'N/A'
        basis = self.parsed.last_value('P_basis')
        if basis is None:
            basis = 'N/A'
        lot = "Method: %s\n" % method
        lot += self.br_tag
        lot += "Basis: %s\n" % basis

        additional_method = self.parsed.last_value('P_additional_method')
        if additional_method:
            lot += self.br_tag + "; ".join(additional_method)
        return self.color_tag(lot, 'lot')

    def excitation(self):
        exc = self.parsed.last_value('P_excitation')
        if exc is not None:
            s = "Electronic Excitation: %s\n" % exc
            return self.color_tag(s, 'lot')

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
        if self.parsed.last_value('P_open_shell')=='UHF':
            return "Open Shell (UHF); S2= %s,\n" % self.parsed.last_value('P_S2')
        elif self.parsed.last_value('P_open_shell')=='ROHF':
            return self.color_tag("ROHF\n",'lot')

    def scf_energy_html(self):
        try:
            return "Last Total Energy= %-11.6f\n" % float(self.parsed.last_value('P_scf_e'))
        except TypeError:
            return "Total Energy %s\n" % self.color_tag('N/A','err')

    def composite_energy_html(self):
        e0 = self.parsed.last_value('P_composite_energy_0')
        eT = self.parsed.last_value('P_composite_energy_T')
        H = self.parsed.last_value('P_composite_enthalpy')
        G = self.parsed.last_value('P_composite_free_energy')
        if e0 is None:
            return 'No E(0K) available'
        names = ('E(0K)','E(T)','H','G')
        s = self.br_tag.join('%s= %s'%v for v in zip(names,(e0,eT,H,G)))
        return self.strong_tag('Composite Method Energies') + self.br_tag + s

    def energy_html(self):
        out = [self.strong_tag('Last Energy Values:')]
        energy_names = self.parsed.find_keys(r'P_.*_energy$')
        if energy_names is None:
            return

        unique_names = list()
        [unique_names.append(x) for x in energy_names if x not in unique_names]

        if 'P_composite_free_energy' in unique_names:
            return self.composite_energy_html()
        for key in unique_names:
            val = self.parsed.last_value(key)
            s = re.search(r'P_(.*)_energy',key).group(1)
            # format parentheses
            sre = re.search(r'(.*)(_p)(.)(p)',s)
            if sre:
                s = '%s(%s)' % (sre.group(1),sre.group(3))
            # format brackets
            sre = re.search(r'(.*)(_b)(.*)(b)',s)
            if sre:
                s = '%s[%s]' % (sre.group(1),sre.group(3))
            en_type = self.parsed.last_value(key+'_type')
            if en_type is not None:
                s += '(%s)' % en_type
            s_en = '%s: %s' % (s.replace('_','-').upper(),val)
            out.append(s_en)
        return self.br_tag.join(out)

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

    def warnings(self):
        wrn = self.parsed.last_value('P_warnings')
        if wrn is not None and wrn:
            s = self.br_tag.join(wrn)
            return self.color_tag(s,'err')


    def report_text(self):
        pass

    def report_html(self):
        self.add_left(self.we.initiate_jmol_applet()) # initialize an JSMol applet
        out_html = [
            #self.jobtype_html(),
            self.level_of_theory_html(),
            self.excitation(),
            self.solvent_html(),
            self.fragmentation_html(),
            self.open_shell_html(),
            self.symmetry_html(),
            self.charge_mult_html(),
            self.scf_failed_html(),
            self.energy_html(),
            # self.scf_energy_html(),
            # self.coupled_cluster_html(),
            self.t1_diagnostics_html(),
            self.warnings()
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