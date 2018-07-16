import subprocess
import os
from itertools import compress
from Top import Top
from Tools.misc import is_number

import logging
log = logging.getLogger(__name__)


class Plot(Top):

    def __init__(self, fname=None, xlab='x', ylab='y', legend=None, x=None, y=None):
        self.save_plot = self.dummy_save_func
        super().__init__()

        self.fname = fname
        self.xlab = xlab
        self.ylab = ylab
        self.legend = legend
        #
        self.choose_plotting_method()  # based on the priority and availability
        #
        self.x = []
        self.y = []
        self.nonempty = self.prepare_data(x, y)
        if len(self.x) < 2:
            logging.info('Only one data point is available, skipping plot')
            self.save_plot = self.dummy_save_func
            self.nonempty = False

        self.real_path = self.settings.real_path(fname)
        self.web_path = self.settings.web_path(fname)

    @staticmethod
    def is_matplotlib_available():
        import importlib.util
        return bool(importlib.util.find_spec("matplotlib"))  # works for python 3.4+

    def is_gnuplot_available(self):
        from shutil import which  # works for Python 3.3+
        return bool(which(self.settings.gnuplot))

    def choose_plotting_method(self):
        """
        Chooses to use gnuplot or matplotlib based on priority and availability
        :return:
        """
        methods = [('gnuplot', self.is_gnuplot_available(), self.save_gnuplot),
                   ('matplotlib', self.is_matplotlib_available(), self.save_matplotlib)]
        #
        if self.settings.preferred_plotting_method == 'matplotlib':
            methods = reversed(methods)
        #
        for method, is_available, func in methods:
            if is_available:
                self.save_plot = func
                return

    @staticmethod
    def dummy_save_func():
        return ''

    def save_matplotlib(self):
        from matplotlib import pyplot as plt

        try:
            for y in self.y:
                plt.plot(self.x, y, marker='o')
            plt.xlabel(self.xlab)
            plt.ylabel(self.ylab)

            # Make a dummy legend
            if (not self.legend) or (len(self.legend) != len(self.y)):
                log.debug('Legend was not provided or contains wrong number of elements')
            else:
                plt.legend(self.legend)
            #
            plt.savefig(self.real_path)
            plt.close()
            log.debug('Picture was saved to %s' % self.real_path)
        except:
            log.error('Cannot create or save matplotlib plot')
            return ''
        return self.web_path

    def save_gnuplot(self):
        log.debug('Starting gnuplot')

        s  = "set term png\n"
        s += "set xlabel '%s'\n" % self.xlab
        s += "set ylabel '%s'\n" % self.ylab
        s += "set output '%s'\n" % self.real_path

        # Write the legend
        if not self.legend or (len(self.legend) != len(self.y)):
            log.debug('Legend was not provided or contains wrong number of elements')
            self.legend = ('-',) * len(self.y)
        pl = "'-' with lp title '%s'," * len(self.y) % tuple(self.legend)
        #
        # Write the data to plot
        s += "plot %s\n" % pl[:-1]

        for y in self.y:
            for i in range(len(self.x)):
                s += "%f %f\n" % (self.x[i], y[i])
            s += "e\n"
        s += "quit\n"
        try:
            with open(self.real_path+'.gp', "w") as text_file:
                text_file.write(s)
            os.system("%s %s" % (self.settings.gnuplot,self.real_path+'.gp'))
        except:
            log.error('Gnuplot picture was not created')

        log.debug('Picture was saved to %s' % self.real_path)
        return self.web_path

    def save_gnuplot_old(self):
        log.debug('Starting gnuplot')
        # Start gnuplot if we can
        try:
            proc = subprocess.Popen([self.settings.gnuplot, '-p'],
                                    shell=True,
                                    stdin=subprocess.PIPE,
                                    stderr=subprocess.PIPE
                                    )
        except:
            log.error('Cannot open gnuplot')
            return ''

        # Shortcut function
        def toGP(s):
            # proc.stdin.write(s)
            # print(s[:-1])  # for debugging Gnuplot
            proc.stdin.write(bytes(s, 'utf-8'))

        try:
            #
            # Write the header
            toGP("set term png\n")
            toGP("ket xlabel '%s'\n" % self.xlab)
            toGP("set ylabel '%s'\n" % self.ylab)
            toGP("set output '%s'\n" % self.real_path)
            #
            # Write the legend
            if not self.legend or (len(self.legend) != len(self.y)):
                log.debug('Legend was not provided or contains wrong number of elements')
                self.legend = ('-',) * len(self.y)
            pl = "'-' with lp title '%s'," * len(self.y) % tuple(self.legend)
            #
            # Write the data to plot
            toGP("plot %s\n" % (pl[:-1]))
            for y in self.y:
                for i in range(len(self.x)):
                    toGP('%f %f\n' % (self.x[i], y[i]))
                toGP('e\n')
            toGP("quit\n")
        except:
            log.error('Gnuplot picture was not created')

        log.debug('Picture was saved to %s' % self.real_path)
        return self.web_path

    def prepare_data(self, x, y):
        """
        check x and y arrays before plotting and,
        if needed, trims them to the same length
        :param x: 1D list/tuple
        :param y: 1D or 2D list/tuple
        """
        if not y:
            return

        # if y is a list, convert it into a list of lists
        if not isinstance(y[0], (list, tuple)): y = [y, ]

        npoints = len(y[0])

        # create x if absent
        if not x: x = range(1, npoints + 1)

        # make a table containing column x and column(s) y
        xy = [x] + list(y) # it could be a tuple from zip

        # Filter only complete rows
        # 1. get a boolean mask whether each element can be converted to number
        vb = list(map(lambda v: list(map(is_number, v)), xy))

        # 2. request all True by rows
        good_rows = list(map(all, zip(*vb)))
        if not good_rows:
            return

        # 3. apply the mask on transposed xy
        t_xy = list(compress(zip(*xy), good_rows))

        # 4. transpose back to the original shape; the result is still in string
        str_xy = list(zip(*t_xy))

        # convert to double
        new_xy = list(map(lambda v: list(map(float, v)), str_xy))

        self.x, self.y = new_xy[:1][0], new_xy[1:]
        return True


if __name__ == "__main__":
    import sys
    sys.path.append('..')

    from Settings import Settings
    Top.settings = Settings()

    fname = 'x.png'
    p = Plot(fname=fname, x=[1, 2, 3, 4], y=[[11, 12, 13, 14], [11, 13, 15, 17]])
    # p = Plot(fname=fname, x=[1, 2, 3, 4], y=[[11, 12, 13, 14]], settings=Settings())
    print(p.settings.real_path(fname))
    p.save_plot()
    # p.save_gnuplot()
    # p.save_matplotlib()
