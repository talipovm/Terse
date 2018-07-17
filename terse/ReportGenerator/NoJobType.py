from ReportGenerator.Geom import Geom
from ReportComponents.Plot import Plot
from ReportGenerator.Top import Top_ReportGenerator
from ReportComponents.WebFile import WebFile

import logging
log = logging.getLogger(__name__)

class NoJobType(Top_ReportGenerator):
    def __init__(self,we,parsed):
        super().__init__(we,parsed)

    def prepare_for_report(self):
        pass

    def save_geom(self):
        G = str(Geom(self.we,self.parsed))
        if not G:
            return
        return WebFile(fname='.xyz',content=G).write()

    def load_in_jmol(self, webpath):
        cmd = [
            self.we.jmol_load_file(webpath),
            self.we.jmol_text('Input (?) geometry')
            ]
        return "; ".join(cmd)

    def report_text(self):
        pass

    def report_html(self):
        webpath = self.save_geom()
        if webpath:
            load_command = self.load_in_jmol(webpath)
            out_html = [
                self.we.jmol_command_to_html(load_command), # load immediately
                'Unrecognized step: ',
                self.we.html_button(load_command, '???'), # and create button to load (useful for several step-jobs)
                self.br_tag
            ]
            [self.add_left(s) for s in out_html]
        else:
            self.add_left(self.color_tag('No coordinates found!','err'))

        return self.get_cells()