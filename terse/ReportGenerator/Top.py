from Top import Top
import Tools.HTML

import logging
log = logging.getLogger(__name__)

class Top_ReportGenerator(Top):
    def __init__(self,we,parsed):
        super().__init__()
        self.we = we
        self.parsed = parsed
        self.prepare_for_report()
        self.report_mode = 'html'
        if self.report_mode=='html':
            self.report = self.report_html
            self.br_tag = Tools.HTML.br
            self.img_tag = Tools.HTML.img
            self.color_tag = Tools.HTML.color
            self.strong_tag = Tools.HTML.strong
        if self.report_mode=='text':
            self.report = self.report_text
            self.br_tag = lambda s:s
            self.img_tag = lambda s:s
            self.color_tag = lambda s:s
            self.strong_tag = lambda s:s
        self.result = list()

    def prepare_for_report(self):
        raise NotImplementedError

    def report_text(self):
        raise NotImplementedError

    def report_html(self):
        raise NotImplementedError

    def add_both(self, v):
        if v:
            self.result.append(v)
            return True

    def add_left(self, b1):
        if b1 is not None:
            return self.add_both((b1, ''))

    def add_right(self, b2):
        if b2 is not None:
            return self.add_both(('', b2))

    def get_cells(self):
        return ["".join(v) for v in zip(*self.result)]
