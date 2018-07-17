if __name__ == "__main__":
    import sys,os
    append_path = os.path.abspath(sys.argv[0])[:-15]
    print("Append to PYTHONPATH: %s" % (append_path))
    sys.path.append(append_path)

from Tools.file2 import file2
from ElectronicStructure import ElectronicStructure
from Processing.Processing import Processing
from Grammar.Grammar import Grammar
from ReportGenerator.ReportGenerator import ReportGenerator
import os.path

import logging
log = logging.getLogger(__name__)

use_old_pickle = False

class Gamess(ElectronicStructure):
    """
    US GAMESS parser
    Analyzes a multiple-step calculation (not really needed for GAMESS)
    """

    def __init__(self):
        """
        Declares steps (type List)
        """
        super().__init__()
        self.parsing_filename = os.path.join(os.path.dirname(__file__), "parsing-rules/gamess_parsing.txt")
        self.processing_filename = os.path.join(os.path.dirname(__file__), "parsing-rules/gamess_processing.txt")

    def parse(self):
        """
        Parses GAMESS file
        """

        GI = file2(self.parsing_filename)
        FI = file2(self.file)

        if not use_old_pickle:
            G = Grammar(GI, FI)
            G.parse()
            self.G_parsed = G.parsed_container
        else:
            import pickle
            pickle.dump(G.parsed_container, open('Interface/G.p', 'wb'))

        FI.close()
        GI.close()
        log.debug('%s parsed successfully' % (self.file))
        return

    def postprocess(self):
        try:
            PI = file2(self.processing_filename)
            log.debug('%s with the processing instructions was opened for reading' % self.processing_filename)
        except:
            log.error('Cannot open %s for reading' % self.processing_filename)

        if use_old_pickle:
            # For the debugging purposes because it's faster
            import pickle
            self.G_parsed = pickle.load(open('Interface/G.p', 'rb'))

        # When the code is ready uncomment it.
        self.P = Processing(PI=PI, parsed=self.G_parsed)
        self.P.postprocess()
        log.debug('%s postprocessed successfully' % (self.file))


    def webdata(self):
        """
        Returns 2 strings with HTML code
        """
        W = ReportGenerator(processed=self.P.parsed)
        return W.report()

#    def usage(self):
#        for step in self.steps:
#            step.usage()

if __name__ == "__main__":

    DebugLevel = logging.DEBUG
    logging.basicConfig(level=DebugLevel)

    from Settings import Settings
    from Top import Top
    Top.settings = Settings(from_config_file= True)
    Top.settings.selfPath=append_path

    from Tools.HTML import HTML
    WebPage = HTML()
    WebPage.readTemplate()

#    f = Orca()
    # f.file = sys.argv[1]
    #import profile
    #profile.run('f.parse()')
    # f.parse()
    # f.postprocess()
    #print(f.steps[0])
    # b1, b2 = f.webdata()

    #WebPage.addTableRow(str(f.file) + web.brn + b1, b2)
    # WebPage.write()
