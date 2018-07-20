from ReportGenerator.Top_ReportGenerator import Top_ReportGenerator

import logging
log = logging.getLogger(__name__)

class Charges(Top_ReportGenerator):

    def __init__(self,we,parsed):
        super().__init__(we,parsed)

    def prepare_for_report(self):
        self.q_Mulliken = self.parsed.last_value('P_charges_Mulliken')
        self.q_Lowdin = self.parsed.last_value('P_charges_Lowdin')
        self.available = self.q_Mulliken or self.q_Lowdin

    def charges_button(self, load_command, charges, name):
        col_min, col_max = -1.0, 1.0
        script_on = "; ".join([
            "x='%(a)s'",
            "DATA '%(p)s @x'",
            "label %%.%(precision)s[%(p)s]",
            "color atoms %(p)s 'rwb' absolute %(col_min)f %(col_max)f"
        ]) % {
            'a': " ".join(charges),
            'p': 'property_' + name,
            'precision': str(2),
            'col_min': col_min,
            'col_max': col_max
        }
        script_on ="; ".join([load_command,script_on])
        return self.we.html_button(script_on, name)

    def charges_button_off(self):
        return self.we.html_button('label off;color atoms cpk', 'Off')

    def button_bar(self, load_command):
        if not self.available:
            return ''
        if self.q_Mulliken:
            s = self.charges_button(load_command, self.q_Mulliken, 'Mulliken')
            self.add_right(s)

        if self.q_Lowdin:
            s = self.charges_button(load_command, self.q_Lowdin, 'Lowdin')
            self.add_right(s)

        self.add_right(self.charges_button_off())
        self.add_right(self.br_tag)

        return self.get_cells()