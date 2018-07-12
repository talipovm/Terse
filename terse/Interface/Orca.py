import Tools.HTML

if __name__ == "__main__":
    import sys,os
    append_path = os.path.abspath(sys.argv[0])[:-15]
    print("Append to PYTHONPATH: %s" % (append_path))
    sys.path.append(append_path)

import re
import Tools.web as web
from Tools.file2 import file2
from Geometry import Scan,IRC,Geom,ListGeoms
import ElectronicStructure
from Containers import AtomicProps

import logging
log = logging.getLogger(__name__)


class Orca(ElectronicStructure):
    """
    Orca 4 parser
    Analyzes a multiple-step calculation
    """

    def __init__(self):
        """
        Declares steps (type List)
        """
        self.steps = []


    def parse(self):
        """
        Parses Orca file, step by step
        """

        try:
            FI = file2(self.file)
            log.debug('%s was opened for reading' %(self.file))
        except:
            log.error('Cannot open %s for reading' %(self.file))

        while True:
            step = OrcaStep(FI)
            step.parse()
            step.postprocess()
            if step.blanc:
                break
            self.steps.append(step)

        FI.close()
        log.debug('%s parsed successfully' % (self.file))
        return


    def webdata(self):
        """
        Returns 2 strings with HTML code
        """

        we = self.settings.Engine3D()

        b1,b2,bb1,bb2,i = '','','','',1
        MaxGeoms, n_Freq = 0, 0
        b1s = []
        for step in self.steps:
            MaxGeoms = max(MaxGeoms,len(step.geoms))
            if step.vector:
                n_Freq = i
            self.settings.subcounter += 1
            step.statfile = self.settings.real_path('.stat')
            b1, b2 = step.webdata(StartApplet=False)
            labeltext = '%s: %s' %(step.JobType,step.lot)
            b1s.append([b1,labeltext.upper()])
            bb2 += b2
            i += 1

        if b1s:
            bb1 = we.JMolApplet(ExtraScript = b1s[n_Freq-1][0])
            if MaxGeoms > 1:
                bb1 += Tools.HTML.brn + we.html_geom_play_controls()
            if n_Freq:
                bb1 += Tools.HTML.brn + we.html_vibration_switch()
            if len(b1s)>1:
                bb1 += Tools.HTML.brn * 2
                # add buttons for each step
                for b1 in b1s:
                    bb1 += we.html_button(*b1)

        log.debug('webdata generated successfully')
        return bb1, bb2


    def usage(self):
        for step in self.steps:
            step.usage()




class OrcaStep(ElectronicStructure):
    """
    Works with a single calculation step
    """


    def parse(self):
        """
        Actual parsing happens here
        """

        t_ifreq_done = False
        self.all_coords = {}

        s = 'BLANC' # It got to be initialized!
        while not self.FI.eof:
            next(self.FI)
            if self.FI.eof:
                break
            s = self.FI.s.rstrip()

            #
            # ---------------------------------------- Read in cartesian coordinates ----------------------------------
            #
            # Have we found coords?
            enter_coord = False
            if s.find('CARTESIAN COORDINATES (ANGSTROEM)')==0:
                coord_type = 'Cartesian Coordinates (Ang)'
                enter_coord = True

            # If yes, then read them
            if enter_coord:
                try:
                    # Positioning
                    dashes1 = next(self.FI)
                    s = next(self.FI)
                    # Read in coordinates
                    geom = Geom()
                    atnames = []
                    while len(s)>1:
                        xyz = s.strip().split()
                        try:
                            atn, x,y,z = xyz[0], xyz[1],xyz[2],xyz[3]
                        except:
                            log.warning('Error reading coordinates:\n%s' % (s))
                            break
                        atnames.append(atn)
                        geom.coord.append('%s %s %s %s' % (atn,x,y,z))
                        s = next(self.FI)
                    # Add found coordinate to output
                    pc = AtomicProps(attr='atnames',data=atnames)
                    geom.addAtProp(pc,visible=False) # We hide it, because there is no use to show atomic names for each geometry using checkboxes

                    if not coord_type in self.all_coords:
                        self.all_coords[coord_type] = {'all':ListGeoms(),'special':ListGeoms()}

                    self.all_coords[coord_type]['all'].geoms.append(geom)

                except StopIteration:
                    log.warning('EOF while reading geometry')
                    break

            #
            # ------------------------------------------- Route lines -------------------------------------------------
            #
            if s.find('Your calculation utilizes the basis')==0:
                self.basis = s.split()[5]

            if s.find(' Ab initio Hamiltonian  Method')==0:
                self.lot = s.split()[5]

            if s.find(' Exchange Functional')==0:
                self.lot = s.split()[4]

            if s.find('  Correlation Functional')==0:
                s_corr = s.split()[4]
                if s_corr != self.lot:
                    self.lot = s.split()[4] + s_corr

            if s.find('Correlation treatment')==0:
                self.lot = s.split()[3]

            if s.find('Perturbative triple excitations            ... ON')==0:
                self.lot += '(T)'

            if s.find('Calculation of F12 correction              ... ON')==0:
                self.lot += '-F12'

            if s.find('Integral transformation                    ... All integrals via the RI transformation')==0:
                self.lot += '-RI'

            if s.find('K(C) Formation')==0:
                if 'RI' in s and 'RI' in self.lot:
                    self.lot = self.lot.replace('RI',s.split()[3])
                else:
                    self.lot += '+'+s.split()[3]

            if s.find('Hartree-Fock type      HFTyp')==0:
                if s.split()[3]=='UHF':
                    self.openShell = True

            if s.find('T1 diagnostic')==0:
                self.T1_diagnostic = s.split()[3]

            if s.find('E(CCSD(T))                                 ...')==0:
                self.postHF_lot.append('CCSD(T)')
                self.postHF_e.append(s.split()[2])
                self.postHF["CCSD(T)"]=s.split()[2]

            if s.find('E(CCSD)                                    ...')==0:
                self.postHF_lot.append('CCSD')
                self.postHF_e.append(s.split()[2])
                self.postHF["CCSD"]=s.split()[2]

            if s.find('               *           SCF CONVERGED AFTER')==0:
                self.FI.skip_until('Total Energy')
                self.scf_e = float(self.FI.s.split()[3])
                self.scf_done = True
                for ct in self.all_coords.values():
                    if ct['all']:
                        ct['all'][-1].addProp('e', self.scf_e) # TODO Read in something like self.best_e instead!

            # S^2
            if s.find('Expectation value of <S**2>     :')==0:
                s_splitted = s.split()
                before = s_splitted[5]
                self.s2 = before
                for ct in self.all_coords.values():
                    if ct['all']:
                        ct['all'][-1].addProp('s2',self.s2)

            if s.find('                       * Geometry Optimization Run *')==0:
                self.JobType = 'opt'

            if 'opt' in self.JobType:
                if s.find('          ----------------------|Geometry convergence')==0:
                    self.opt_iter += 1
                    try:
                        next(self.FI) # skip_n Item value
                        next(self.FI) # skip_n ------
                        for conv in ('max_force','rms_force','max_displacement','rms_displacement'):
                            s = next(self.FI)
                            x, thr = float(s.split()[2]),float(s.split()[3])
                            conv_param = getattr(self,conv)
                            conv_param.append(x-thr)
                            for ct in self.all_coords.values():
                                if ct['all']:
                                    ct['all'][-1].addProp(conv, x-thr)
                    except:
                        log.warning('EOF in the "Converged?" block')
                        break
                if s.find('                    ***        THE OPTIMIZATION HAS CONVERGED     ***')==0:
                    self.opt_ok = True
            #
            # -------------------------------------------- Scan -------------------------------------------------------
            #
            if s.find('                       *    Relaxed Surface Scan    *')==0:
                self.JobType = 'scan'

            if 'scan' in self.JobType:
                """
                Order of scan-related parameters:
                    1. Geometry,
                    2. Energy calculated for that geometry
                    3. Optimization convergence test
                If Stationary point has been found, we already have geometry with energy attached as prop, so we just pick it up
                """
                # Memorize scan geometries
                if s.find('                    ***        THE OPTIMIZATION HAS CONVERGED     ***')==0:
                    for ct in self.all_coords.values():
                        if ct['all']:
                            ct['special'].geoms.append(ct['all'][-1])
                # Record scanned parameters
                # Designed to work properly only for 1D scans!
                if s.find('         *               RELAXED SURFACE SCAN STEP')==0:
                    next(self.FI)
                    s = next(self.FI)
                    param = s[12:45].strip()
                    # Will work properly only for bonds at this point
                    mt=re.compile('Bond \((.*?),(.*?)\)').match(param)
                    param = 'Bond(' + str(1+int(mt.group(1))) + ',' + str(1+int(mt.group(2))) + ')'

                    param_full = float(s[46:59].strip())
                    #print('|'+s[46:59]+'|'+str(param_full))
                    for ct in self.all_coords.values():
                        if ct['special']:
                            ct['special'][-1].addProp(param,param_full)

            #
            # ---------------------------------------- Read simple values ---------------------------------------------
            #

            #Nproc
            if s.find('           *        Program running with 4') == 0:
                self.n_cores = s.split()[4]

            # Read Symmetry
            if s.find('POINT GROUP')==0:
                self.sym = s.split()[3]

            # Read charge_multmetry
            if s.find('Total Charge           Charge')==0:
                self.charge = s.split(4)
            if s.find('Multiplicity           Mult')==0:
                self.mult = s.split(4)

            if 'ORCA TERMINATED NORMALLY' in s:
                self.OK = True
                next(self.FI)
                break

        # We got here either 
        self.blanc = (s=='BLANC')
        return



    def postprocess(self):
        #
        # ======================================= Postprocessing  ======================================================
        #

        if self.lot_suffix:
            self.lot += self.lot_suffix

        """
        Choose coordinates to show in JMol
        """
        if self.freqs and self.freqs[0]<0:
            order = ('Standard','Input','Cartesian Coordinates (Ang)','Z-Matrix')
        else:
            order = ('Input','Cartesian Coordinates (Ang)','Z-Matrix','Standard')

        n_steps_by_to = {}
        for to in order:
            if to in self.all_coords:
                nst = len(self.all_coords[to]['all'].geoms)
                if nst > self.n_steps:
                    self.n_steps = nst

        # choose geometries to show
        for tp in ('special','all'):
            for to in order:
                if to in self.all_coords and self.all_coords[to][tp]:
                    self.geoms = self.all_coords[to][tp]
                    break
            if self.geoms:
                log.debug('%s orientation used' % (to))
                break
        del self.all_coords

        if 'irc' in self.JobType:
            self.series = IRC(other=self.geoms)
            self.series.direction = self.irc_direction
            self.series.both = self.irc_both
            del self.irc_direction
            del self.irc_both

        if 'scan' in self.JobType:
            self.series = Scan(other=self.geoms)

        if self.freqs and self.geoms:
            if self.OK:
                self.geoms.geoms = [self.geoms[-1],]


        log.debug('Orca step (%s) parsed successfully' %(self.JobType))
        return


    def usage(self):
        s = ''
        s += 'Computation Node: %s\n' % (self.machine_name)
        if hasattr(self,'n_cores'):
            s+= '#Cores: %s\n' % (self.n_cores)
        s += 'Level of Theory: %s\n' % (self.lot)
        s += 'Job type: %s\n' % (self.JobType)
        if self.solvent:
            s += 'Solvent: %s\n' % (self.solvent)
        s += 'Open Shell: %i\n' % (self.openShell)
        s += '#Atoms: %i\n' % (self.n_atoms)
        s += '#Electrons: %i\n' % (self.n_electrons)
        s += '#Gaussian Primitives %i\n' % (self.n_primitives)
        if 'opt' in self.JobType:
            s += '#Opt Steps %s\n' % (self.n_steps)
        if 'td' in self.JobType:
            s += '#Excited States %s\n' % (self.n_states)
        s += '#SU %.1f\n' % (self.time)

        FS = open(self.statfile,'w')
        FS.write(s)
        FS.close()
        #print s


#
#
#
#
#
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

    f = Orca()
    f.file = sys.argv[1]
    #import profile
    #profile.run('f.parse()')
    f.parse()
    f.postprocess()
    #print(f.steps[0])
    b1, b2 = f.webdata()

    WebPage.addTableRow(str(f.file) + Tools.HTML.brn + b1, b2)
    WebPage.write()
