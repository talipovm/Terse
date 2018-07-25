if __name__ == "__main__":
    import sys,os
    append_path = os.path.abspath(sys.argv[0])[:-15]
    print("Append to PYTHONPATH: %s" % (append_path))
    sys.path.append(append_path)

from Tools.file2 import file2
from Top import Top
from Processing.Processing import Processing
from Grammar.Grammar import Grammar
from ReportGenerator.ReportGenerator import ReportGenerator
import os.path

import logging
log = logging.getLogger(__name__)


class Gamess(Top):
    """
    US GAMESS parser
    """

    def __init__(self):
        """
        Declares steps (type List)
        """
        super().__init__()
        self.parsing_filename = os.path.join(os.path.dirname(__file__), "parsing-rules/gamess_parsing.txt")
        self.processing_filename = os.path.join(os.path.dirname(__file__), "parsing-rules/gamess_processing.txt")

    def parse(self):
        GI = file2(self.parsing_filename)
        FI = file2(self.file)

        G = Grammar(GI, FI)
        G.parse()
        self.G_parsed = G.parsed_container

        # import pickle
        # pickle.dump(G.parsed_container, open('Interface/G.p', 'wb'))
        # self.G_parsed = pickle.load(open('Interface/G.p', 'rb'))

        FI.close()
        GI.close()

        log.debug('%s parsed successfully' % (self.file))
        return

    def postprocess(self):

        PI = file2(self.processing_filename)
        self.P = Processing(PI=PI, parsed=self.G_parsed)
        self.P.postprocess()

        # GAMESS-specific edits
        if self.P.parsed.last_value('gbasis') is not None:
            self.postprocess_basis()

        log.debug('%s postprocessed successfully' % self.file)

    def postprocess_basis(self):

        P = self.P.parsed
        basis_words = ('gbasis', 'igauss', 'polar', 'ndfunc', 'nffunc', 'diffsp', 'npfunc', 'diffs')
        vals = list(P.last_value(s) if P.last_value(s) is not None else '' for s in basis_words)
        b = dict(zip(basis_words, vals))

        def polarf(plr, suffix):
            if plr in ('0', ''):
                return ''
            if plr == '1':
                return suffix
            return plr + suffix

        if b['gbasis'] in ('N21', 'N31', 'N311'):
            basis = '%s-%s' % (b['igauss'], b['gbasis'][1:])
            if 'T' in b['diffsp']:
                basis += '+'
                if 'T' in b['diffs']:
                    basis += '+'
            basis += 'G'

            polar_heavy = polarf(b['ndfunc'], 'd') + polarf(b['nffunc'], 'f')
            if polar_heavy:
                polar_H = polarf(b['npfunc'], 'p')
                if polar_H:
                    polar = '(%s,%s)' % (polar_heavy, polar_H)
                else:
                    polar = '(%s)' % polar_heavy
            else:
                polar = ''

            basis += polar
            self.G_parsed.conditionally_add(old_key='P_basis', new_key='P_basis', new_value=basis)

        if b['gbasis'] == 'STO':
            basis = 'STO-%sG' % b['igauss']
            if b['ndfunc'] != '0':
                basis += '*'
            self.G_parsed.conditionally_add(old_key='P_basis', new_key='P_basis', new_value=basis)

    def webdata(self):
        """
        Return 2 strings with HTML code
        """
        W = ReportGenerator(processed=self.P.parsed)
        return W.report()
