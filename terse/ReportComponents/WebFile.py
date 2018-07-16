from Top import Top

import logging
log = logging.getLogger(__name__)

class WebFile(Top):
    def __init__(self,fname=None,content=''):
        super().__init__()
        self.fname = fname
        self.content=content

    def write(self):
        file = self.settings.real_path(self.fname)
        try:
            f = open(file,'w')
        except IOError:
            log.critical('Cannot open file "%s" for writing' % (file))
            return

        f.write(self.content)
        f.close()

        log.debug('Coordinates were written to file ' + file)
        return self.settings.web_path(self.fname)
