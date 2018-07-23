import logging
log = logging.getLogger(__name__)

from ReportGenerator.Job import Job
from ReportGenerator.Top_ReportGenerator import Top_ReportGenerator

class ReportGenerator(Top_ReportGenerator):

    def __init__(self, processed):
        super().__init__(we=self.settings.Engine3D(),parsed=processed)

    def prepare_for_report(self):
        pass

    def report_text(self):
        pass

    def report_html(self):
        jobs = self.parsed.separate('job')
        z = [Job(self.we,p).report() for p in jobs]
        return ["".join(v) for v in zip(*z)]
