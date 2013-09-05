import os

RSYNC_CMD = "rsync -av {0[dflags]} {0[flags]} {0[source]} {0[target]}"
DEFAULT_FLAGS = ["--delete"]

class RsyncError(Exception) : pass

class Rsync(object):
    def __init__(self,source,target,link_dest=None,flags=""):
        self.args = {
            "source" : source,
            "target" : target,
            "dflags" : " ".join(DEFAULT_FLAGS)+" ",
            "flags"  : flags,
        }

        if link_dest != None :
            self.args["dflags"] += "--link-dest={0} ".format(link_dest)

        self.generate()
        self.status = None

    def generate(self):
        self.cmd = RSYNC_CMD.format(self.args)

    def execute(self):
        self.status = os.system(self.cmd)

        if self.status != 0:
            raise RsyncError("rsync exit with status {0} : {1}".format(self.status,self.cmd))
