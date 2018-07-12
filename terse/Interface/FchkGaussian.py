if __name__ == "__main__":
    import sys,os
    selfname = sys.argv[0]
    full_path = os.path.abspath(selfname)[:]
    last_slash = full_path.rfind('/')
    dirpath = full_path[:last_slash] + '/..'
    print("Append to PYTHONPATH: %s" % (dirpath))
    sys.path.append(dirpath)

import time,re,logging,os
import math
import sys
import subprocess
from Interface.Cube import Cube
from ElStr import ElectronicStructure
from Geometry import Geom,ListGeoms,IRC
from Containers import AtomicProps
from Tools import web
from Tools.file2 import file2
log = logging.getLogger(__name__)





class FchkGaussian(ElectronicStructure):
    """
    Shows 3D-properties from the .fchk file
    """
    def __init__(self):
        self.densities = []
        self.openshell = False
        self.cubes = []
        self.isotype=''
        self.isovalue='0.03'
        ElectronicStructure.__init__(self)
        self.OK = True


    def makeCube(self,prop,name='',colors=''):
        fcube = self.settings.real_path(prop + '.cube')
        wpcube = self.settings.web_path(prop + '.cube')

        command = (self.settings.cubegen, self.settings.nproc, prop, self.file, fcube, self.settings.npoints_cube, 'h')
        str_command = " ".join(map(str, command))

        t1 = time.time()
        log.debug('Trying to run command: "%s"' % (str_command) )
        subprocess.call(map(str,command))
        t2 = time.time()
        log.debug('Running cubegen: %.1f s' % (t2-t1))

        if os.path.exists(fcube):
            log.debug('%s successfully generated' % (fcube))
        else:
            log.warning('%s has not been created' % (fcube))

        c = Cube(name,colors)
        c.file = fcube
        c.wpcube = wpcube
        c.isotype = prop.split('=')[0]
        c.isovalue = self.isovalue
        c.parse()
        return c


    def parse(self):
        """
        Here, .fchk will be parsed as a text file
        Probably, we start here, because .fchk contains valuable
        information which might be used
        """

        try:
            FI = file2(self.file)
        except:
            log.error('Cannot open %s for reading' %(self.file))

        """
        http://www.gaussian.com/g_tech/g_ur/f_formchk.htm

        All other data contained in the file is located in a labeled line/section set up in one of the following forms:
            Scalar values appear on the same line as their data label. This line consists of a string describing the data item, a flag indicating the data type, and finally the value:
                Integer scalars: Name,I,IValue, using format A40,3X,A1,5X,I12.
                Real scalars: Name,R,Value, using format A40,3X,A1,5X,E22.15.
                Character string scalars: Name,C,Value, using format A40,3X,A1,5X,A12.
                Logical scalars: Name,L,Value, using format A40,3X,A1,5X,L1.
            Vector and array data sections begin with a line naming the data and giving the type and number of values, followed by the data on one or more succeeding lines (as needed):
                Integer arrays: Name,I,Num, using format A40,3X,A1,3X,'N=',I12. The N= indicates that this is an array, and the string is followed by the number of values. The array elements then follow starting on the next line in format 6I12.
                Real arrays: Name,R,Num, using format A40,3X,A1,3X,'N=',I12, where the N= string again indicates an array and is followed by the number of elements. The elements themselves follow on succeeding lines in format 5E16.8. Note that the Real format has been chosen to ensure that at least one space is present between elements, to facilitate reading the data in C.
                Character string arrays (first type): Name,C,Num, using format A40,3X,A1,3X,'N=',I12, where the N= string indicates an array and is followed by the number of elements. The elements themselves follow on succeeding lines in format 5A12.
                Character string arrays (second type): Name,H,Num, using format A40,3X,A1,3X,'N=',I12, where the N= string indicates an array and is followed by the number of elements. The elements themselves follow on succeeding lines in format 9A8.
                Logical arrays: Name,H,Num, using format A40,3X,A1,3X,'N=',I12, where the N= string indicates an array and is followed by the number of elements. The elements themselves follow on succeeding lines in format 72L1.
            All quantities are in atomic units and in the standard orientation, if that was determined by the Gaussian run. Standard orientation is seldom an interesting visual perspective, but it is the natural orientation for the vector fields. 
        """
        def split_array(s,reclength):
            v = []
            nrec = int(math.ceil((len(s)-1.0)/reclength))
            for i in range(nrec):
                rec = s[reclength*i:reclength*(i+1)].strip()
                v.append(rec)
            return v

        self.parsedProps = {}
        format_arrays = {
                'I' : [6.,12],
                'R' : [5.,16],
                'C' : [5.,12],
                'H' : [9.,8],
                }
        try:
            self.comments = next(FI).rstrip()
            s = next(FI).rstrip()
            self.JobType, self.lot, self.basis = s[0:10],s[10:20],s[70:80]
            while True:
                s = next(FI)
                if FI.eof:
                    break
                s = s.rstrip()
                array_mark = (s[47:49] == 'N=')
                if array_mark:
                    value = []
                    prop, vtype, nrec = s[:40].strip(), s[43], int(s[49:])
                    fa = format_arrays[vtype]

                    nlines = int(math.ceil(nrec/fa[0]))
                    for _ in range(nlines):
                        s = next(FI)
                        v5 = split_array(s,fa[1])
                        value.extend(v5)
                else:
                    prop, vtype, value = s[:40].strip(), s[43], s[49:].strip()
                self.parsedProps[prop] = value
        except StopIteration:
            log.warning('Unexpected EOF')

        FI.close()
        log.debug('%s parsed successfully' % (self.file))
        return



    def postprocess(self):
        #
        def any_nonzero(ar):
            for s in ar:
                if float(s)!=0:
                    return True
            return False
        #
        def getGeom(ar,atnum,atnames,start=0):
            Bohr = 0.52917721
            g = Geom()
            atbase = start
            for i in range(atnum):
                atn = atnames[i]
                xyz = ar[atbase:atbase+3]
                x, y, z = list(map(lambda k: float(k)*Bohr, xyz))
                g.coord.append('%s %f %f %f' % (atn,x,y,z))
                atbase += 3
            pc = AtomicProps(attr='atnames',data=atnames)
            g.addAtProp(pc,visible=False) # We hide it, because there is no use to show atomic names for each geometry using checkboxes
            return g
        #
        def getHOMOcharges(shell_to_atom_map,shell_types,n_el,mos,basis_size):
            #
            def rep(v1,v2):
                new = []
                for i in range(0,len(v1)):
                        for _ in range(v2[i]):
                                    new.append(v1[i])
                return new
            #
            def dict_values_sorted_by_key(d):
                v = []
                for k in sorted(d.keys()):
                    v.append(d[k])
                return v
            #
            # Shell types (NShell values): 0=s, 1=p, -1=sp, 2=6d, -2=5d, 3=10f, -3=7f
            shell_codes = {'0':1,'1':3,'-1':4,'2':6,'-2':5,'3':10,'-3':7,'4':14,'-4':9}
            #
            # get #primitives for each shell
            n_basis_func_per_shell = [shell_codes[k] for k in shell_types]
            #print('shell_to_atom_map',shell_to_atom_map)
            #print('Shell types',shell_types)
            #print('n_basis_func_per_shell',n_basis_func_per_shell)
            #
            # assign each primitive to atom index
            atom_map_HOMO = rep(shell_to_atom_map, n_basis_func_per_shell)
            #print('atom_map_HOMO',atom_map_HOMO)
            #
            if len(atom_map_HOMO) != basis_size:
                log.error('Size of HOMO does not match number of primitives')

            #
            homo = mos[(basis_size*(n_el-1)):(basis_size*n_el)]
            homo2 = [float(c)**2 for c in homo]
            norm = sum(homo2)
            norm_homo2 = [c2/norm for c2 in homo2]
            #print(norm)
            #print('norm_homo2',norm_homo2)

            c2_per_atom = {}
            for i_atom,c2 in zip(atom_map_HOMO,norm_homo2):
                int_i_atom = int(i_atom)
                if int_i_atom in c2_per_atom.keys():
                    c2_per_atom[int_i_atom] += c2
                else:
                    c2_per_atom[int_i_atom] = c2

            #print('c2_per_atom',c2_per_atom)
            sc2 = dict_values_sorted_by_key(c2_per_atom)
            #print('sc2',sc2)
            return sc2
        #
        def old_getHOMOcharges(at_numbers,atnames,n_el,mos,basis_size):
            #
            def accumu(lis):
                total = 0
                yield total
                for x in lis:
                    total += x
                    yield total
            #
            def homo_atom_contr(at_basis_cum,i):
                # atom numbering starts from 0
                squares = [float(c)**2 for c in homo[at_basis_cum[i]:at_basis_cum[i+1]]]
                return sum(squares)
            #
            # Shell types (NShell values): 0=s, 1=p, -1=sp, 2=6d, -2=5d, 3=10f, -3=7f
            n_basis_per_shell = {'0':1,'1':3,'-1':4,'2':6,'-2':5,'3':10,'-3':7}
            basis_funcs = {"6":15,"7":15,"8":15,"1":2,"35":30} # Specific for 6-31G(d) 6d!
            #
            at_basis = [basis_funcs[at_type] for at_type in at_numbers]
            at_basis_cum = list(accumu(at_basis))
            #
            homo = mos[(basis_size*(n_el-1)):(basis_size*n_el)]
            norm_homo = sum([float(c)**2 for c in homo])

            squares = [homo_atom_contr(at_basis_cum,i)/norm_homo for i in range(0,len(at_numbers))]
            return squares
        #
        pp = self.parsedProps
        self.charge = pp['Charge']
        self.mult = pp['Multiplicity']
        self.sym = 'NA'
        self.solvent = 'NA'
        if 'S**2' in pp:
            s2_before = float(pp['S**2'])
            s2_after  = float(pp['S**2 after annihilation'])
            if s2_before > 0.0:
                self.openshell = True
            self.s2 = '%.4f / %.4f' % (s2_before,s2_after)
        if any_nonzero(pp['External E-field']):
            self.extra += 'External Electric Field applied'
        self.scf_e = float(pp['SCF Energy'])
        self.total_e = pp['Total Energy']

        atnames = list(map(lambda k: int(float(k)), pp['Nuclear charges']))
        atnum = int(pp['Number of atoms'])

        at_numbers = pp["Atomic numbers"]
        n_el = int(pp["Number of alpha electrons"])
        mos = pp["Alpha MO coefficients"]
        basis_size = len(pp["Alpha Orbital Energies"])

        self.geoms = ListGeoms()

        is_irc = ('IRC point       1 Geometries' in pp)
        is_opt = ('Opt point       1 Geometries' in pp) & False # It might be rather confusing than useful thing, so I'll turn it off for a while

        if is_irc:
            self.JobType += ' (irc)'
            ngeom = int(pp['IRC Number of geometries'][0])
            shift = int(pp['IRC Num geometry variables'])
            irc_ex = pp['IRC point       1 Results for each geome']
            base,exi = 0,0
            for i in range(ngeom):
                g = getGeom(pp['IRC point       1 Geometries'],atnum,atnames,base)
                e,x = irc_ex[exi:exi+2]
                g.addProp('x',float(x))
                g.addProp('e',float(e))
                g.to_kcalmol = 627.509
                self.geoms.append(g)
                base += shift
                exi += 2
            self.series = IRC(other=self.geoms)
        elif is_opt:
            ngeom = int(pp['Optimization Number of geometries'][0])
            shift = int(pp['Optimization Num geometry variables'])
            opt_ez = pp['Opt point       1 Results for each geome']
            base,ezi = 0,0
            for i in range(ngeom):
                g = getGeom(pp['Opt point       1 Geometries'],atnum,atnames,base)
                e,z = opt_ez[ezi:ezi+2]
                g.addProp('e',float(e))
                g.to_kcalmol = 627.509
                self.geoms.append(g)
                base += shift
                ezi += 2
        else:
            g = getGeom(pp['Current cartesian coordinates'],atnum,atnames)
            # Parse charges
            for k in pp:
                if ' Charges' in k:
                    ch = k[:k.find(' ')]
                    charges = pp[k]
                    if any_nonzero(charges):
                        pc = AtomicProps(attr=ch,data = charges)
                        g.addAtProp(pc)

            # Add HOMO Charges
            homo_charges = getHOMOcharges(pp['Shell to atom map'],pp['Shell types'],n_el,mos,basis_size)
            pc = AtomicProps(attr='HOMO_charges',data = homo_charges)
            g.addAtProp(pc)

            # Record geometry
            self.geoms.append(g)

        d_types = ['SCF','MP2','CI','QCI']
        for k in pp:
            # Energies
            if ' Energy' in k:
                et = k[:k.find(' ')]
                e = pp[k]
                if et == 'SCF':
                    continue
                self.extra += '%s: %.8f' %(k,float(e)) + web.brn
            # Densities
            for dt in d_types:
                if ('Total %s Density' % dt) in k:
                    self.densities.append(dt)



    def generateAllCubes(self):
        # {A,B}MO=HOMO LUMO ALL OccA OccB Valence Virtuals
        # Laplacian
        dprops = ['Density', 'Potential']

        if self.openshell:
            dprops.append('Spin')
            props = ['AMO=HOMO','BMO=HOMO','AMO=LUMO','BMO=LUMO']
        else:
            props = ['MO=HOMO','MO=LUMO']

        for d in self.densities:
            for p in dprops:
                prop = '%s=%s' % (p,d)
                c = self.makeCube(prop)
                self.cubes.append((c,prop))
        for p in props:
            c = self.makeCube(p)
            self.cubes.append((c,p))


    def webdata(self):
        we = self.settings.Engine3D()
        b1,b2 = ElectronicStructure.webdata(self)
        if self.settings.detailed_print:
            # Show all cubes
            self.generateAllCubes()
            s = ''
            for c,p in self.cubes:
                first_cube = c.wpcube
                ctype = p[:p.find('=')]
                if ctype == 'Density':
                    continue
                elif ctype == 'Potential':
                    first_cube = c.wpcube.replace('Potential','Density')
                    second_cube = c.wpcube
                    script = we.jmol_isosurface(webpath = first_cube, webpath_other = second_cube, surftype=ctype)
                else:
                    script = c.s_script
                s += we.html_button(action=script, label=p)
            b2 += s
        elif self.isotype:
            # Show only requested cube
            p = self.isotype.lower()
            p_splitted = p.split('=')
            ctype = p_splitted[0]
            if len(p_splitted)>1:
                cvalue = p_splitted[1]

            if ctype == 'potential':
                p_pot  = p
                p_dens = p.replace('potential','Density')

                c_pot = self.makeCube(p_pot)
                c_dens = self.makeCube(p_dens)

                first_cube = c_dens.wpcube
                second_cube = c_pot.wpcube
                script = we.jmol_isosurface(webpath = first_cube, webpath_other = second_cube, surftype=ctype)
            else:
                c = self.makeCube(p)
                script = c.s_script
                if ctype=='mo':
                    if cvalue=='homo':
                        cvalue = self.parsedProps['Number of alpha electrons']
                    if cvalue=='lumo':
                        cvalue = int(self.parsedProps['Number of alpha electrons'])+1
                    e_orb = float(self.parsedProps['Alpha Orbital Energies'][int(cvalue)-1])*27.211
                    b2 += 'E(AMO) = %.3f eV' % (e_orb)
                if ctype=='amo':
                    e_orb = float(self.parsedProps['Alpha Orbital Energies'][int(cvalue)-1])*27.211
                    b2 += 'E(AMO) = %.3f eV' % (e_orb)
                if ctype=='bmo':
                    e_orb = float(self.parsedProps['Beta Orbital Energies'][int(cvalue)-1])*27.211
                    b2 += 'E(BMO) = %.3f eV' % (e_orb)

            b2 += we.html_button(action=script, label=p)
            b2 += we.html_button('isosurface off', 'Off')

        return b1,b2
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

    f = FchkGaussian()
    f.file = sys.argv[1]
    f.parse()

    for k in sorted(f.parsedProps):
        v = f.parsedProps[k]
        if isinstance(v,list):
            print('"%s": array of %i elements; first elements is %s' % (k,len(v),v[0]))
        else:
            print('"%s": %s' % (k, str(v)))
    #f.makeCube('Density=SCF')
