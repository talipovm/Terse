from Tools.ChemicalInfo import BohrR, to_element_name
from ReportGenerator.Top_ReportGenerator import Top_ReportGenerator
import Tools.misc as misc

import logging
log = logging.getLogger(__name__)

class Geom(Top_ReportGenerator):

    def __init__(self,we,parsed,show_vibration=None,start_skip=0,end_skip=0):
        # super().__init__(we,parsed) # cannot call it
        self.we = we
        self.parsed = parsed
        self.bohr_units = self.parsed.last_value('P_geom_bohr') != 'empty'
        self.geom_raw = self.parsed.last_value('P_geom')
        self.geom = list()
        self.show_vibration = show_vibration
        self.comment = ''
        self.coord = list()
        self.vibs = list()
        self.vectors = list()
        self.start_skip=start_skip
        self.end_skip=end_skip
        self.prepare_for_report()
        self.prepare_comments()

    def prepare_for_report(self):
        if self.geom_raw is None:
            return None
        for atom_raw in self.geom_raw:
            atom = atom_raw.copy()
            atom[0] = to_element_name(atom[0])
            if self.bohr_units:
                atom[1:] = [str(float(q)*BohrR) for q in atom[1:]]
            self.geom.append(atom)
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
        del self.vibs[self.start_skip:self.end_skip]
        self.vectors = [' '.join(dq) for dq in self.vibs[self.show_vibration]]
        return

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