from ReportGenerator.Geom import Geom
from ReportGenerator.Top_ReportGenerator import Top_ReportGenerator
from ReportComponents.WebFile import WebFile
from ReportGenerator.Charges import Charges
import itertools

import logging
log = logging.getLogger(__name__)

class Freq(Top_ReportGenerator):
    def __init__(self,we,parsed):
        self.im_freq = False
        super().__init__(we,parsed)

    def prepare_for_report(self):
        freq = self.parsed

        self.term_ok = (freq.last_value('P_term_ok')== 'True')

        start_skip_freq = freq.last_value('P_start_skip_freq')
        if start_skip_freq is None:
            self.start_skip_freq = 0
        else:
            self.start_skip_freq = int(start_skip_freq)-1

        end_skip_freq = freq.last_value('P_end_skip_freq')
        if end_skip_freq is None:
            self.end_skip_freq = 6
        else:
            self.end_skip_freq = int(end_skip_freq)

        start_im_freq = freq.last_value('P_start_im_freq')
        if start_im_freq is None:
            self.start_im_freq = None
        else:
            self.start_im_freq = int(start_im_freq)-1

        end_im_freq = freq.last_value('P_end_im_freq')
        if end_im_freq is None:
            self.end_im_freq = None
        else:
            self.end_im_freq = int(end_skip_freq)

        self.freqs_cm = None
        self.im_freq = None
        if freq.last_value('P_freqs') is not None:
            # useful when GAMESS prints out one freq per row
            self.freqs_cm = [float(fr[0]) for fr in freq.last_value('P_freqs')]

        if freq.last_value('P_freqs_horizontal') is not None:
            # useful when GAMESS prints out five freqs in a row
            L = [item[0] for item in freq.get_value('P_freqs_horizontal')]
            self.freqs_cm = [float(fr) for fr in itertools.chain(*L)]

        if self.freqs_cm:
            if self.end_im_freq is not None:
                for i in range(self.start_im_freq,self.end_im_freq):
                    self.freqs_cm[i] *= -1
            del self.freqs_cm[self.start_skip_freq:self.end_skip_freq]
            self.im_freq = (self.freqs_cm[0]<0)

        self.prepare_thermochem()
        self.charges = Charges(self.we,self.parsed)

    def prepare_thermochem(self):
        freq = self.parsed
        T = freq.get_value('P_thermo_temp')
        E_corr = freq.get_value('P_thermo_e_corr')
        H_corr = freq.get_value('P_thermo_h_corr')
        G_corr = freq.get_value('P_thermo_g_corr')
        self.thermochem_units = freq.last_value('P_thermo_units')
        self.thermochem_available = len(T)>0
        if self.thermochem_available:
            self.thermochem = zip(*[T, E_corr, H_corr, G_corr])

    def freq_range(self):
        s = "Freqs: "
        i = 0
        while self.freqs_cm[i] < 0:
            s_freq = "%.1f," % self.freqs_cm[i]
            if i == 0:
                s += self.color_tag(s_freq, 'imag')
            else:
                s += self.color_tag(s_freq, 'err')
            i += 1
        if i < len(self.freqs_cm)-1:
            s += "%.1f .. %.1f\n" % (self.freqs_cm[i], self.freqs_cm[-1])
        elif i == len(self.freqs_cm)-1:
            s += "%.1f\n" % self.freqs_cm[i]
        return s

    def save_geom(self):
        if self.im_freq:
            nvib = 0
        else:
            nvib = None
        G = str(Geom(self.we, self.parsed, show_vibration=nvib,start_skip=self.start_skip_freq,end_skip=self.end_skip_freq))
        if not G:
            return ''
        return WebFile(fname='-freq.xyz', content=G).write()

    def load_in_jmol(self, webpath):
        cmd  = [
            self.we.jmol_load_file(webpath),
            self.we.jmol_text('Vibrational analysis')
            ]
        return "; ".join(cmd)

    def thermochem_html(self):
        s = self.strong_tag("Thermochemical corrections:")
        s += self.br_tag
        for v in self.thermochem:
            s += "T=%s: E= %s, H= %s, G= %s (%s)\n" % (v+(self.thermochem_units,))
            s += self.br_tag
        return s

    def jobtype_html(self):
        sx = self.strong_tag('FREQ')
        if self.term_ok:
            return sx
        else:
            return self.color_tag(sx, 'err')

    def report_text(self):
        pass

    def report_html(self):

        webpath = self.save_geom()
        if webpath:
            load_command = self.load_in_jmol(webpath)

            out_html = [
                self.we.jmol_command_to_html(load_command), # load immediately
                'Frequency step: ',
                self.we.html_button(load_command, 'Freq') # and create button to load (useful for several step-jobs)
            ]
            [self.add_left(s) for s in out_html]

            if self.im_freq:
                self.add_left(self.we.html_vibration_switch())
                self.add_left(self.br_tag)
        else:
            self.add_left(self.color_tag('No coordinates found!','err'))

        self.add_right(self.jobtype_html())
        self.add_right(self.br_tag)

        if self.freqs_cm:
            self.add_right(self.freq_range())
            self.add_right(self.br_tag)

        if self.im_freq:
            self.add_right(self.color_tag('Imaginary Freq(s) found!', 'imag'))
            self.add_right(self.br_tag)

        if self.thermochem_available:
            self.add_right(self.thermochem_html())

        if webpath and self.charges is not None:
            self.add_both(self.charges.button_bar(load_command))

        return self.get_cells()