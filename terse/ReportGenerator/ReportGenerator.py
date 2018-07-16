import logging
log = logging.getLogger(__name__)

from ReportGenerator.Job import Job
from ReportGenerator.Top import Top_ReportGenerator

class ReportGenerator(Top_ReportGenerator):

    def __init__(self, processed):
        super().__init__(we=self.settings.Engine3D(),parsed=processed)

    def prepare_for_report(self):
        self.do_multijob = (self.parsed.aggregate_name == 'job')

    def report_text(self):
        pass

    def report_html(self):
        if self.do_multijob:
            jobs = self.parsed
        else:
            jobs = [self.parsed]
        z = [Job(self.we,p).report() for p in jobs]
        return ["".join(v) for v in zip(*z)]
