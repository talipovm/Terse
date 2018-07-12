import logging
import os

from Interface.Isosurface import Isosurface
from Interface.JVXL import JVXL
from Interface.NBOinteractions import NBOinteractions
from Top import Top

log = logging.getLogger(__name__)


class ParserFactory(Top):

    @staticmethod
    def interface_by_command_line(frecord):
        """
        Assign a class to a task from the group_names dictionary
        """
        rectype, params = frecord[0], frecord[1:]
        if rectype == 'file':
            return

        type2class = {
            'inbo': NBOinteractions,
            'iso': Isosurface,
            'jvxl': JVXL,
            'top': Top
        }
        if rectype in type2class:
            parser = type2class[rectype]()
            log.debug('Assigned parser was successfully loaded')
            return parser
        else:
            log.error("Parser '%s' cannot be loaded" % parser)
            return Top()

    @staticmethod
    def interface_by_file_extension(frecord, exts):
        """
        Assign a class to frecord
        """
        rectype, params = frecord[0], frecord[1:]
        if rectype != 'file':
            return

        top = Top()
        file = params[0]
        base, ext = os.path.splitext(file)
        ext = ext[1:]
        if ext in exts:
            ParsingClass = exts[ext]
            log.info('%s parser is selected for %s' % (ParsingClass, file))
        else:
            log.error("Extension '%s' is not registered" % ext)
            return top

        ModName = 'Interface.' + ParsingClass
        try:
            GenericParser = __import__(ModName)
            module = getattr(GenericParser, ParsingClass)
        except:
            log.error("Module '%s' cannot be loaded" % ModName)
            return top

        try:
            cl = eval('module.' + ParsingClass)()
            log.debug('Assigned parser was successfully loaded')
            return cl
        except NameError:
            log.error("Parser '%s' cannot be loaded" % ParsingClass)
            return top

    @staticmethod
    def typeByContent(frecord):
        # TODO To be implemented
        rectype, params = frecord[0], frecord[1:]
        return Top()
