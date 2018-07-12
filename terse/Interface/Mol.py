if __name__ == "__main__":
    import sys

    sys.path.append('..')

import logging

import Geometry
from Top import Top

log = logging.getLogger(__name__)


class Mol(Top):
    def __init__(self):
        super().__init__()
        self.vector = []
        self.noAtoms = 0
        self.geoms = Geometry.ListGeoms()
        self.scan = None
        self.wp = ''

    def write(self, fname, geoms, topologies=None):
        """
        writes MOL file.
        Terse uses two file formats:
            1. MDL Molfile
                '+': Supports topology
            2. XYZ
                '+': Simple, easier to reuse
                '+': JMol supports extended format with vectors
            Normally, XYZ format is used. However, if there are no vibrational modes in the output file and NBO topology found,
        Molfile format can be used. (Not implemented)
        """

        file = self.settings.real_path(fname)
        if not geoms:
            log.warning('File %s: No coordinates to write!' % file)
            return
        try:
            f = open(file, 'w')
        except IOError:
            log.critical('Cannot open file "%s" for writing' % file)
            return
        """
        e= -567.757342394   R(2,5)= 1.7
         OpenBabel07311213123D

          7  6  0  0  0  0  0  0  0  0999 V2000
           -1.2474    0.9235    0.0001 C   0  0  0  0  0  0  0  0  0  0  0  0
           -0.5334   -0.7125    0.0000 S   0  0  0  0  0  0  0  0  0  0  0  0
           -1.8521    1.0687   -0.8932 H   0  0  0  0  0  0  0  0  0  0  0  0
           -0.4079    1.6259   -0.0001 H   0  0  0  0  0  0  0  0  0  0  0  0
            1.1456   -0.4465    0.0000 N   0  0  0  0  0  0  0  0  0  0  0  0
            1.5606    0.6706    0.0001 O   0  0  0  0  0  0  0  0  0  0  0  0
           -1.8518    1.0688    0.8936 H   0  0  0  0  0  0  0  0  0  0  0  0
          1  7  1  0  0  0  0
          2  5  1  0  0  0  0
          2  1  1  0  0  0  0
          3  1  1  0  0  0  0
          4  1  1  0  0  0  0
          5  6  2  0  0  0  0
        M  END
        """

        """
        Remarks:
            # only 1 geometry supported
            # no comments supported
        """
        if len(geoms) > 1:
            log.warning('Only one geometry per file is supported')
        geom = geoms[0]
        comment = geom.propsToString(ShowComment=True)
        sg = '%s\n%s\n\n' % (file, comment)

        nb = 0
        for a1 in topologies:
            nb += len(a1)
        sg += "%3s %3s  0  0  0  0  0  0  0  0999 V2000" % (len(geom), nb)
        for at in geom.coord:
            el, x, y, z = at.split()
            sg += "%10.4f%10.4f%10.4f %-2s   0  0  0  0  0  0  0  0  0  0  0  0\n" % (x, y, z, el)
        for a1 in topologies.keys():
            for a2 in topologies[a1].keys():
                sg += '%3s%3s  %1s  0  0  0  0\n' % (a1, a2, topologies[a1][a2])
        sg += ' M  END\n$$$$\n'

        f.write(sg)
        f.close()
        return


#
#
#
if __name__ == "__main__":
    DebugLevel = logging.DEBUG
    logging.basicConfig(level=DebugLevel)

    from Settings import Settings

    Top.settings = Settings(from_config_file=True)

    f = Mol()
    f.file = sys.argv[1]
