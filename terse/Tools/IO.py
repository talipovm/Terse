"""
This module is responsible for writing, moving, and deleting files
"""
import glob
import logging
import os
import subprocess
import time

log = logging.getLogger(__name__)


def is_readable(f):
    if os.access(f, os.R_OK):
        log.debug('File %s is readable' % f)
        return True
    else:
        log.error('File %s is not readable' % f)
        return False


def all_readable(files):
    for f1 in files:
        if not is_readable(f1):
            return False
    return True


def is_writable(f):
    if os.access(f, os.W_OK):
        log.debug('File %s is writable' % f)
        return True
    else:
        log.error('File %s is not writable' % f)
        return False


def clean_folder(d):
    """
    :rtype:
    """
    files = glob.glob(d + '/*')
    try:
        for f in files:
            os.remove(f)
    except OSError:
        log.warning('Unable to clean up ' + d)
        return False
    log.debug(d + ' cleaned up')
    return True


def prepare_folder(d):
    if not d:
        log.critical('Output folder has not been set in settings')
        return False
    if os.path.exists(d):
        if not os.access(d, os.W_OK):
            log.critical(d + ' exists but not writable')
            return False
    else:
        log.warning(d + ' does not exist')
        try:
            os.mkdir(d)
            log.warning(d + ' created')
        except OSError:
            log.critical(d + ' cannot be created')
            return False
    return True


def remove_cubes_from_tersepic(d):
    files = glob.glob(d + '/*.cube')
    try:
        for f in files:
            os.remove(f)
    except OSError:
        log.warning('Unable to clean up cube files ' + d)
        return False
    log.debug(d + ' cleaned up')
    return True


# def backupdir(d):
#    if os.path.exists(d):
#        if not os.access(d,os.W_OK):
#            log.critical(d + ' exists but not writable')
#            return False
#    else:
#        log.warning(d + ' does not exist')
#        try:
#            os.mkdir(d)
#            log.warning(d + ' created')
#        except:
#            log.critical(d + ' can not be created')
#            return False
#    return True

def execute_Jmol(jmol_abs_path, script):
    # Create temporary file
    tmp_fname = '/tmp/%sterse.tmp' % (os.environ['USER'])  # Make a better filename!
    FI = open(tmp_fname, 'w')
    # Write script in that file
    FI.write(script)
    FI.close()

    runjmol = '/bin/sh %s/jmol.sh -s %s -n' % (jmol_abs_path, tmp_fname)
    # Run JMol
    t1 = time.time()
    log.debug('Trying to run command: ' + runjmol)
    subprocess.call(runjmol.split())
    t2 = time.time()
    log.debug('Done in %.1f s' % (t2 - t1))
