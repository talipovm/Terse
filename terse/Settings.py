import logging
import os
import re
import copy
import time
from argparse import ArgumentParser, RawTextHelpFormatter, SUPPRESS
from datetime import datetime
import os
from Top import Top

log = logging.getLogger(__name__)


# noinspection PyShadowingNames
class Settings(Top):
    """
    Parses settings in the following order:
    1) Built-in settings
    2) Settings from self.configfile
    3) If command line option --config=configfile is present, read settings from configfile
    4) Settings from the command line options
    Settings from the previous steps can be overwritten.
    """

    def __init__(self, from_config_file=True):
        # self.OutputFolder = os.environ['HOME']+'/Sites/'
        super().__init__()

        self.settings = None # settings is the only class that does not need settings attribute

        ### Default settings ###
        self.OutputFolder = os.environ['HOME'] + '/public_html/'
        # self.BackupFolder = os.environ['HOME']+'/Sites/terse-backup/'

        # sub-folder name for storing xyz and png files for HTML page
        self.tersepic = 'terse-pics/'

#        self.configFile = os.path.join(os.path.dirname(__file__), "data/terse.rc")
        self.configFile = os.path.join(os.environ['HOME'], "terse.rc")

        #self.configFile = '/Users/talipovm/Dropbox/development/terse/terse.rc'

        self.tersehtml = 'terse.html'

        # Relative location of Jmol folder with respect to self.tersehtml
        # Should be within the web server folders
        self.JmolFolder = './Jmol/'

        # Debug run
        self.debug = False

        # Prints out additional information about CPU usage for each calculation
        self.usage = False

        # Current folder from which terse.py is invoked
        self.selfPath = ''

        # Options from the command line interface
        self.optsCLI = {}

        # Number of available CPUs
        # Not in use currently but might be used to parallelize e.g. cubegen
        self.nproc = 0

        # File extension <-> Parsing interface matching
        self.exts = {}

        # Time stamp -- used to produce unique xyz/png file names and avoid problems
        # with undesired use of cached old files.
        # Now, it is probably not needed since HTML page itself prevents caching
        self.suffix = time.strftime('%y-%m-%d--%H-%M-%S')

        # A timestamp to be shown on the web page
        self.timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")

        self.EnergyUnits = 'kJ/mol'
        self.EnergyFactor = 2625.5

        # Threshold for strong/weak inter-orbital interactions
        self.inbo_threshold = 10.0

        # Show the set of internal coordinates (not implemented yet)
        self.connectivityMode = 0

        # Request to show all geometries from geometry optimization
        # even when geometry optimization was successful
        self.FullGeomInfo = False

        # Was used to print out IRC energies
        # self.textirc = False

        # Show IRC gradients?
        self.ircgrad = 0

        # Request to print detailed information (e.g. for str(object)
        self.detailed_print = False

        # Counters to keep track of the log files and jobs within them
        self.counter = 1
        self.subcounter = 0

        # Number of points if a cube file is requested (e.g. for orbital or ESP)
        self.npoints_cube = '0'

        # Store surface plots as isosurfaces in JVXL format rather than volumetric cube files
        # Cube files are huge and very slow to show on a web page
        self.useJVXL = True

        # Remove cube files after .jvxl files were produced
        self.save_cube = False

        # Default orbital colors
        self.color_mo_plus = 'red'
        self.color_mo_minus = 'blue'

        # Default path to gnuplot for making png; [TODO] to be replaced by matplotlib
        self.preferred_plotting_method = 'gnuplot'
        self.gnuplot = 'gnuplot' # if gnuplot will try to find it in PATH

        # Path to Gaussian utilities for making orbital/ESP plots
        self.cubegen = 'cubegen'
        self.formchk = 'formchk'

        self.color = {'err':'red', 'imag':'blue', 'lot':'green'}

        from Engine3D import JSMol
        self.Engine3D = JSMol
        # self.JSMolLocation = "http://comp.chem.mu.edu"
        self.JSMolLocation = ''

        # Applet window dimensions
        self.JmolWinX, self.JmolWinY = 800, 600

        # Molecule representation in Jmol
        self.JavaOptions = """vector ON; vector SCALE 3;\\
        set animationFPS 10;\\
        set measurementUnits pm;\\
        set measureAllModels ON;\\
        wireframe 20; spacefill 40;\\
        """

        # Overwrite the built-in parameters by those from the provided config file
        if from_config_file:
            self.read_config()

    def set_arg_val(self, line):
        """
        Imports attr=value to settings. It will be accessible as settings.attr
        """
        s = re.search(r'\s*(\S+)\s*=\s*(.*)', line)
        if s:
            attr = s.group(1)
            value = s.group(2)
            setattr(self, attr, value)

    def read_config(self, configfile=''):
        """
        Read configuration file
        """
        if configfile:
            fname = configfile
        else:
            fname = self.configFile
        try:
            f = open(fname, 'r')
            for s in f:
                if '#' in s: s = s.split('#')[0]  # Strip comments
                self.set_arg_val(s)
            f.close()
            log.debug('Configuration file %s was successfully loaded' % fname)
        except IOError:
            log.warning("Cannot open config file " + fname)

    def float(self):  # TODO convert the input data into proper type on the fly
        for a, v in self.__dict__.items():
            try:
                fv = float(v)
                setattr(self, a, fv)
            except TypeError:
                pass

    @staticmethod
    def expand_range(s):
        """
        Converts an input string that looks like '3,15-17,20' into an expanded
        list [3,15,16,17,20]
        :param s:
        :return: list
        """
        if not s: return []
        s_out = []
        for item in s.split(','):
            if '-' in item:
                range_start, range_end = item.split('-')
                for i_mo in range(int(range_start), int(range_end) + 1):
                    s_out.append(i_mo)
            else:
                s_out.append(int(item))
        return s_out

    def prepare_filenames(self):
        if not ('filenames' in self.optsCLI):
            log.error('No files provided')
            return []
        fnames = self.optsCLI['filenames']
        if not isinstance(fnames, list):
            fnames = [fnames, ]
        return fnames

    def parse_shortcuts(self):
        """
        Recognizes simplified input and applies to all files.
        At this moment, the files are assumed to be checkpoint files
        :param optsCLI:
        :return: list of tasks
        """
        rec = {}
        # Make an +/-0.001 au isovalue spin density plot for all files in the command line
        rec['spin'] = {'type': 'spin', 'iv': 0.001}
        # Make an +0.001 au (i.e. only positive) isovalue spin density plot for all tasks in the command line
        rec['spin2'] = {'type': 'spin2', 'iv': 0.001}
        # Make a  +/-0.03 au isovalue HOMO plot for all tasks in the command line
        rec['homo'] = {'type': 'mo=homo', 'iv': 0.03}
        # Make a  +/-0.03 au isovalue LUMO plot for all tasks in the command line
        rec['lumo'] = {'type': 'mo=lumo', 'iv': 0.03}

        tasks = []

        fnames = self.prepare_filenames()
        if not fnames: return []

        for key, item in rec.items():
            if key in self.optsCLI:
                for fn in fnames:
                    item = copy.deepcopy(item)
                    item['c'] = fn
                    tasks.append(('iso', item))
        return tasks

    def parse_by_orb_range(self):
        """
        Recognizes simplified input of plotting a series of molecular orbitals
        :param optsCLI:
        :return:
        """
        rec = {}
        # Make a  +/-0.03 au isovalue plots for MOs selected by indices (starting from 1)
        rec['mos'] = {'type': 'mo=%i', 'iv': 0.03}
        # Make a  +/-0.03 au isovalue plots for _alpha_ MOs selected by indices (starting from 1)
        rec['amos'] = {'type': 'amo=%i', 'iv': 0.03}
        # Make a  +/-0.03 au isovalue plots for _beta_ MOs selected by indices (starting from 1)
        rec['bmos'] = {'type': 'bmo=%i', 'iv': 0.03}
        # for all files in the command line

        tasks = []

        fnames = self.prepare_filenames()
        if not fnames: return []

        for key, item in rec.items():
            if key in self.optsCLI:
                mo_range = self.expand_range(self.optsCLI[key])
                for fname in fnames:
                    item['c'] = fname
                    for mo in mo_range:
                        item2 = copy.deepcopy(item)
                        item2['type'] %= mo
                        tasks.append(('iso', item2))
        return tasks

    def parse_extensions(self):
        # Register extensions
        for attr, value in self:
            if '_extension' in attr:
                progname = attr.strip().split('_extension')[0]
                values = value.replace(' ', '').split(',')
                for v in values:
                    if v in self.exts:
                        log.warning('Several parsers for %s requested; will use the last_value request, %s' %(v, progname))
                    else:
                        self.exts[v] = progname
        log.debug('Registered extensions: %s' % self.exts)
        return self.exts

    @staticmethod
    def parse_CLI_list(CLI_list, dict_name, leading_symbol):
        """
        Combines a dictionary-type command line argument as dictionary:
        Recognized input:
            0. Single record, simple syntax: --inbo a.chk (i.e., CLI_list=['a.chk']; leading_symbol='c')
            1. Single record, key/value pair(s): --inbo c=a.chk --inbo l=a.log;
                    (i.e., CLI_list=['c=a.chk', 'l=a.log']; leading_symbol will be parsed from that)
            2. Multiple records, e.g. --inbo c1=a.chk --inbo l1=a.log --inbo c2=b.chk --inbo l2=b.log
                    (i.e., CLI_list=['c1=a.chk', 'l1=a.log', 'c2=b.chk', 'l2=b.log'];
                    leading_symbol will be parsed from that)
        """
        implicit_counter = 0
        tasks = []
        jobs = {}
        for arg in CLI_list:
            # Separate keys from values
            ssplit = arg.split('=', 1)
            if len(ssplit) == 1:
                # Deal with simplified input 1.
                key, value = leading_symbol, ssplit[0]
            else:
                key, value = ssplit

            if re.search('^' + leading_symbol, key):
                implicit_counter += 1
            # If job index is not provided, use implicit counter
            if not re.search(r'\d+', key):
                key += str(implicit_counter)
            # Split keys by job numbers
            k, i = re.search(r'^(\D+)(\d+)$', key).groups()
            i = int(i)
            if not (i in jobs): jobs[i] = {}
            jobs[i][k] = value
        for job in sorted(jobs):
            tasks.append((dict_name, jobs[job]))
        return tasks

    def parse_full_syntax_lists(self):
        """
        Converts dictionary-type command-line arguments into tasks
        :param optsCLI:
        :return:
        """
        rec = []
        # full isosurface syntax for a checkpoint file
        rec.append({'type': 'isosurface', 'name': 'iso', 'ls': 'c'})
        # full isosurface syntax for a formatted checkpoint file TODO figure out why it was commented out
        # rec.append({'type':'isosurface', 'name':'iso', 'ls': 'f'})
        # inbo TODO: recollect how to use them
        rec.append({'type': 'inbo', 'name': 'inbo', 'ls': 'l'})
        # full isosurface syntax for a JVXL
        rec.append({'type': 'jvxl', 'name': 'jvxl', 'ls': 'j'})

        tasks = []
        for v in rec:
            if not v['type'] in self.optsCLI:
                continue
            task = self.parse_CLI_list(CLI_list=self.optsCLI[v['type']], dict_name=v['name'], leading_symbol=v['ls'])
            tasks.extend(task)
        return tasks

    def parse_command_line(self, args):
        """
        Parse command line parameters
        """

        descr = """
        terse.py - Helps to perform express visual analysis of output files of
                   electronic structure calculations (mostly, Gaussian).
                   The main idea of this script is to collect results of multiple calculations
                   in one HTML file. For each calculation, short text description of each step will be given,
                   and most important geometries will be shown in 3D mode using Jmol inside the web page.
        Features:
                   Visualization of multiple files on the same web page
                   Extensive support of Gaussian package
                   Basic support of US-Gamess, Firefly packages
                   Gzipped files supported
        Requirements:
                   Python (also need argparse 'pip install argparse')
                   OpenBabel (must install with python bindings and png)
                   Gnuplot (optional, used for convergence/Scan/IRC plot generation)
                   Jmol  (to show molecules in 3D mode on the web page)
                   JSMol (to show molecules in 3D mode on the web page using javascript)
        Author:
                   Marat Talipov, talipovm@nmsu.edu
        """
        sp = args[0]
        self.selfPath = sp[:sp.rfind('/') + 1]
        ar = args[1:]

        parser = ArgumentParser(descr, formatter_class=RawTextHelpFormatter, argument_default=SUPPRESS)
        parser.add_argument('--connectivityMode', action='store_true', help='Show set of internal coordinates')
        parser.add_argument('--debug', action='store_true', help='Debug mode')
        parser.add_argument('--config', action='store', help='Path to config file')
        parser.add_argument('--usage', action='store_true', help='Shows small statistics on CPU usage')
        parser.add_argument('--detailed_print', action='store_true', help='Show more detailed information')
        parser.add_argument('--inbo',
                            help='Show interacting NBO orbitals; specially arranged Gaussian calculation needed,\nneeds two keys, "l" and "c"(optional key "t").\nUsage: terse.py --inbo l=LOGFILE --inbo c=CHECKPOINTFILE\nOptional usage: --inbo t=NBOENERGYTHRESHHOLD(default is 10 kcal/mol)',
                            action='append', default=[])
        parser.add_argument('--jvxl', help='Show JVXL isosurface, needs two keys, "j" and "x"', action='append',
                            default=[])
        parser.add_argument('--isosurface', help='Show isosurface from Gaussian .chk file', action='append', default=[])
        parser.add_argument('--settings', help='Redefine settings', action='append', default=[])
        parser.add_argument('--OutputFolder',
                            help='Write terse pages to local folder in Sites. Useful for saving\nterse pages to some local archive.\nUsage: terse.py --OutputFolder=$HOME/Sites/PATH_TO_ARCHIVE_DIR',
                            action='store')
        parser.add_argument('--spin', help='Show spin density', action='store_true')
        parser.add_argument('--spin2', help='Show spin density without negative polarization (red) lobes',
                            action='store_true')
        parser.add_argument('--homo', help='Show HOMO', action='store_true')
        parser.add_argument('--lumo', help='Show LUMO', action='store_true')
        parser.add_argument('--mos', help='Show selected MOs', action='store')
        parser.add_argument('--amos', help='Show selected alpha-MOs', action='store')
        parser.add_argument('--bmos', help='Show selected beta-MOs', action='store')
        parser.add_argument('filenames', nargs='*', help='Files to parse')
        # parser.add_argument('--rmcube', help='Remove cube files from DIR after JVXL created', action='store_true')
        # parser.add_argument('--backup', help='Backup Mode: Create web page in backup directory for later use',action='store')
        # parser.add_argument('irc', help='Force terse.pl to consider two files as the part of the same IRC calculation')
        # parser.add_argument('uv', help='Show interacting NBO orbitals')

        self.optsCLI = vars(parser.parse_args(ar))

        # Update settings from a user-provided config file
        if 'config' in self.optsCLI:
            self.read_config(self.optsCLI['config'])

        # Additional settings could be chimed in using --setting attr=value mechanism
        if 'settings' in self.optsCLI:
            for opt in self.optsCLI['settings']:
                self.set_arg_val(opt)

        # Update the settings directly requested from CLI
        for attr in ('detailed_print', 'debug', 'usage', 'OutputFolder'):
            if attr in self.optsCLI:
                setattr(self, attr, self.optsCLI[attr])

        # Incorporate the syntax shortcut options above into the list of tasks to be processed
        tasks = self.parse_shortcuts()
        tasks_defined = bool(tasks)
        if not tasks_defined:
            tasks = self.parse_by_orb_range()
            tasks_defined = bool(tasks)
        if not tasks_defined:
            # Regular tasks
            fnames = self.prepare_filenames()
            for f in fnames:
                tasks.append(('file', f))
            tasks.extend(self.parse_full_syntax_lists())
        return tasks

    def real_path(self, fname):
        s = '%s/%s/%s--%i-%i%s' % (self.OutputFolder, self.tersepic, self.suffix, self.counter, self.subcounter, fname)
        return s

    def web_path(self, fname):
        s = './%s/%s--%i-%i%s' % (self.tersepic, self.suffix, self.counter, self.subcounter, fname)
        return s


if __name__ == "__main__":
    print("Test output")
    print("\n===Hard-coded settings:===")
    s = Settings(from_config_file=False)
    print(s)
    print("\n===Settings updated from config file (%s)===" % s.configFile)
    s.read_config()
    print(s)
    print("\n===Settings updated from the command line===")
    import sys

    files = s.parse_command_line(sys.argv)
    print(s)
    print(files)
