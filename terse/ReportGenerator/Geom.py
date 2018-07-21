from Tools.ChemicalInfo import BohrR, to_element_name
from ReportGenerator.Top_ReportGenerator import Top_ReportGenerator
import Tools.misc as misc

import logging
log = logging.getLogger(__name__)

class Geom(Top_ReportGenerator):

    def __init__(self,we,parsed,show_vibration=None):
        # super().__init__(we,parsed) # cannot call it
        self.we = we
        self.parsed = parsed
        self.bohr_units = self.parsed.last_value('P_geom_bohr') != 'empty'
        self.geom = self.parsed.last_value('P_geom')
        self.show_vibration = show_vibration
        self.comment = ''
        self.coord = list()
        self.vibs = list()
        self.vectors = list()
        self.prepare_for_report()
        self.prepare_comments()

    def prepare_for_report(self):
        if self.geom is None:
            return None
        for atom in self.geom:
            atom[0] = to_element_name(atom[0])
            if self.bohr_units:
                atom[1:] = [str(float(q)*BohrR) for q in atom[1:]]
        self.coord = [' '.join(atom) for atom in self.geom]

        if self.show_vibration is not None:
            self.prepare_vibrations()

    def prepare_comments(self):
        # TODO extract s2, scan/IRC and convert into comment line
        P_scf_e = self.parsed.last_value('P_scf_e')
        if P_scf_e is not None:
            self.comment = "SCF_Energy= %-11.6f " % float(P_scf_e)

    def prepare_vibrations(self):
        # Reformat frequencies
        self.vibs = []
        all_displacement = self.parsed.get_value('P_vibrations')
        if all_displacement is not None:
            for vs in all_displacement:
                for v in zip(*vs):
                    self.vibs.append(misc.split(v, 3))
        self.vectors = [' '.join(dq) for dq in self.vibs[self.show_vibration]]

    def __str__(self):
        if not self.coord:
            log.warning('No coordinates to write!')
            return ''

        n_atoms = len(self.coord)
        if self.vectors:
            if n_atoms!=len(self.vectors):
                log.warning('Number of atoms is different from !')
            coords = ["  ".join(v) for v in zip(self.coord,self.vectors)]
        else:
            coords = self.coord

        return "\n".join([str(n_atoms),self.comment]+coords)