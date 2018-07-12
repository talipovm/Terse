from Geometry import ListGeoms

import logging
log = logging.getLogger(__name__)

class Scan(ListGeoms):

    def webdata(self, SortGeom = False):
        self.ces = self.toBaseLine(EnFactor=float(self.settings.EnergyFactor))
        s = ''
        for prop in self.props:
            if (prop == 'e') or (prop == 's2'):
                x = []
            else:
                x = getattr(self, prop)
            s = self.plot(x=x, xlabel=prop, y=[self.ces])
            s += self.extrema(title='Scan min/max points :',yg=self.ces,frame_names=x,frame_prefix=prop+'=')
        return s
