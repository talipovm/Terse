import Tools.HTML

if __name__ == "__main__":
    import sys,os
    selfname = sys.argv[0]
    full_path = os.path.abspath(selfname)[:]
    last_slash = full_path.rfind('/')
    dirpath = full_path[:last_slash] + '/..'
    print("Append to PYTHONPATH: %s" % (dirpath))
    sys.path.append(dirpath)

import logging
from ReportComponents.Plot import Plot
from Top import Top
import Interface.XYZ

log = logging.getLogger(__name__)

class ListGeoms(Top):
    """
    Basically, it is a container of 3D structures, each of them of class Geom()
    """

    def __init__(self,other=None):
        if other:
            # BUG is here
            self.geoms = other.geoms
            self.props = other.props
            self.atprops = other.atprops
        else:
            self.geoms = []


    def __nonzero__(self):
        """
        Returns true if contains any geometries
        """
        return bool(self.geoms)


    def __len__(self):
        """
        Return: number of structures
        """
        return len(self.geoms)


    def __iter__(self):
        """
        Iterates over geometries
        """
        return self.geoms.__iter__()



    def __getattr__(self,a,FloatOnly=False):
        """
        returns: parameter values collected from all geometries
        rtype: list (or string, if 'comment' was requested)
        """

        if a == 'comment':
            return self.mergeComments()
        if a == 'props':
            if self.geoms:
                return self[0].props
            else:
                return []
        r = []
        for g in self.geoms:
            try: # Do we have this attribute?
                v = getattr(g,a)
                if FloatOnly:
                    if type(v) is float:
                        r.append(v)
                    else:
                        r.append('')
                else:
                    r.append(v)
            except:
                r.append('')
        return r


    def __contains__(self,item):
        """
        To test if parameter is defined, looks into parameters of the first geometry
        """
        return (item in self[0])


    def __getitem__(self,item):
        """
        Picks geometry by index
        return: Geometry
        rtype: Geom()
        """
        return self.geoms[item]


    def addProp(self,a,v):
        if not a in self.props:
            self.props.append(a)
        setattr(self,a,v)

    def addAtProp(self,a,v):
        if not a in self.atprops:
            self.atprops.append(a)
        setattr(self,a,v)

    def append(self,geom):
        """
        Appends geometry to container
        """

        self.geoms.append(geom)


    def mergeComments(self):
        """
        Collects comments from each structures
        return: merged string with comments
        rtype: string
        """
        out = [g.comment for g in self.geoms if g.comment.strip()]
        return Tools.HTML.br.join(out) + Tools.HTML.br

    def consistencyCheck(self):
        """
        Tests if number of atoms corresponds to the number of atom in header and
        if all geometries have the same number of atoms
        """

        g0 = self[0]
        for i,g in enumerate(self.geoms):
            if g.header_natoms != len(g.coord):
                log.warning('Number of atoms in header in geometry %i does not match to actual value' % (i+1))
                return False
            if g.header_natoms != g0.header_natoms:
                log.warning('Number of atoms in models 1 and %i is not the same' % (i+1))
                return False
        return True

    def plot(self,xlabel='Scan point',ylabel='',x=None,y=None):
        io = Plot()
        if not ylabel:
            ylabel = 'E, %s' % (self.settings.EnergyUnits)
        if not y:
            y = self.toBaseLine()
        plt = Plot('.png', xlab=xlabel, ylab=ylabel, x=x, y=y)
        plt.save_plot()
        return Tools.HTML.img(plt.web_path)

    def extrema(self,title='Min/Max points:',yg=None,naround=3,show_min=True,show_max=True,frame_names = None, frame_prefix='Point '):
        """
        Make buttons corresponding to min/max
        """

        we = self.settings.Engine3D()
        s = Tools.HTML.br + title + Tools.HTML.br
        s += we.html_button('Frame 1', 'First')
        lyg = len(yg)
        #print yg
        if not frame_names:
            frame_names = range(1,lyg+1)
        for i in range(1,lyg-1):
            i_left, i_right = i-naround, i+naround+1
            if i_left < 0:
                i_left = 0
            if i_right >= lyg:
                i_right = lyg
            around =  yg[i_left:i_right]
            i_min_around = min(range(len(around)),key=around.__getitem__)
            i_max_around = max(range(len(around)),key=around.__getitem__)

            is_min =  show_min and (i == i_left + i_min_around)
            is_max =  show_max and (i == i_left + i_max_around)
            #print i,i_left,i_right,around,is_min,is_max
            if (is_min or is_max):
                nframe = 'Frame %s' % (i+1) # Frame numbers start from 1
                npoint = frame_prefix + str(frame_names[i])
                s += we.html_button(nframe, npoint)
        s += we.html_button('Frame %s' % (lyg), 'Last')
        return s


    def toBaseLine(self,mine=None,EnFactor=None):
        if not self.e:
            return []
        if not EnFactor:
            EnFactor = float(self.settings.EnergyFactor)

        if self.e[-1]=='': # takes care of the case when last_value opt step was unsuccessful, and energy is not available
            es = self.e[:-1]
        else:
            es = self.e

        if not mine:
            if len(es)>0:
                mine = min(es)
            else:
                mine = 0

        ces = []
        for e in es:
            ce = (e - mine) * EnFactor
            ces.append(ce)
        return ces


    def sortAlongX(self,mapd):
        d = []
        for a in mapd:
            arr = getattr(self,a)
            d.append(arr)
        #print(d)
        d2 = list(zip(*sorted(zip(*d))))
        #print(d2)
        if not d2:
            return
        for i in range(len(mapd)):
            a,v = mapd[i],d2[i]
            setattr(self,a,v)


    def write(self,fname,vectors=None):
        c = Interface.XYZ.XYZ()
        webpath = c.write(fname,geoms=self.geoms,vectors=vectors)
        return webpath
