from ReportGenerator.Top_ReportGenerator import Top_ReportGenerator
from ReportGenerator.Geom import Geom

import logging
log = logging.getLogger(__name__)

class Charges(Top_ReportGenerator):

    def __init__(self,we,parsed):
        self.Q = list()
        super().__init__(we,parsed)

    def prepare_for_report(self):
        geom = Geom(self.we,self.parsed).geom
        q_Mulliken = self.parsed.last_value('P_charges_Mulliken')
        q_Lowdin = self.parsed.last_value('P_charges_Lowdin')
        Q = (
            (q_Mulliken, 'Mulliken'),
            (self.combineH(q_Mulliken, geom), 'no_H'),
            (q_Lowdin, 'Lowdin'),
            (self.combineH(q_Lowdin, geom), 'no_H'),
        )
        self.Q = list((q,name) for q,name in Q if q is not None)
        self.available = (len(list(self.Q))>0)

    def combineH(self, q, geom):
        if (geom is None) or (q is None) or ([atom for atom in geom if atom[0]!='H'] is None):
            return None
        out = [float(x) for x in q]
        at_pairs = self.assignH(geom)
        for i,j in at_pairs:
            out[j] += out[i]
            out[i] = 0
        return [str(x) for x in out]

    def assignH(self, geom):
        return [(i,self.find_closest(i,geom)) for i,atom in enumerate(geom) if atom[0]=='H']

    def find_closest(self,i,geom):
        x,y,z = [float(q) for q in geom[i][1:]]
        min_r2 = 1e6
        min_j = 0
        for j,at2 in enumerate(geom):
            if at2[0]=='H' or i==j:
                continue
            x2,y2,z2 = [float(q) for q in at2[1:]]
            r = (x2-x)**2 + (y2-y)**2 + (z2-z)**2
            if r < min_r2:
                min_r2 = r
                min_j = j
        return min_j

    def charges_button(self, load_command, charges, name):
        color_min, color_max = -1.0, 1.0
        h_1 = h_2 = ""
        if 'no_H' in name:
            h_1 = "color atoms cpk; label off ; select not Hydrogen"
            h_2 = "select all"

        script_on = "; ".join([
            "x='%(a)s'",
            "DATA '%(p)s @x'",
            "%(h_1)s",
            "label %%.%(precision)s[%(p)s]",
            #"color atoms %(p)s 'rwb' absolute %(col_min)f %(col_max)f",
            "%(h_2)s"
        ]) % {
            'a': " ".join(charges),
            'p': 'property_' + name,
            'precision': str(2),
            'col_min': color_min,
            'col_max': color_max,
            'h_1': h_1,
            'h_2': h_2
        }
        script_on ="; ".join([load_command,script_on])
        return self.we.html_button(script_on, name)

    def charges_button_off(self):
        return self.we.html_button('label off;color atoms cpk', 'Off')

    def button_bar(self, load_command):
        if not self.available:
            return ''

        self.add_right('Charges: ')

        for q,name in self.Q:
            s = self.charges_button(load_command, q, name)
            self.add_right(s)

        self.add_right(self.charges_button_off())
        self.add_right(self.br_tag)

        return self.get_cells()