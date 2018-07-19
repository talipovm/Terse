from Top import Top

import logging
log = logging.getLogger(__name__)


class Top_Grammar(Top):
    def __init__(self, GI, FI, parsed_container=None, troublemakers=None):
        super().__init__()
        self.GI = GI
        self.FI = FI
        self.parsed_container = parsed_container
        self.troublemakers = troublemakers

    def execute(self):
        raise NotImplementedError