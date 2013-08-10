import os

RSYNC_CMD = "rsync -avP {0[dflags]} {0[flags]} {0[source]} {0[target]}"

class Rsync(object):
    def __init__(self,source,target,link_dest=None,flags=""):
        self.args = {
            "source" : source,
            "target" : target,
            "dflags" : "--delete",
            "flags"  : flags,
        }

        if link_dest != None :
            self.args["flags"] += "--link-dest={0}".format(link_dest)

        self.generate()
        self.status = None

    def generate(self):
        self.cmd = RSYNC_CMD.format(self.args)

    def execute(self):
        self.status = os.system(self.cmd)

#r = Rsync("/tmp/target","/tmp/backup/v1")
#r = Rsync("/tmp/target","/tmp/backup/v1","/tmp/backup/v0")
#r.cmd += " -n --stats"
#print r.cmd

#r.execute()
