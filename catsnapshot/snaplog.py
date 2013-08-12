from datetime import datetime
from dateutil import tz
import os,sys

LOG_DATETIME_FORMAT = "%Y%m%d%H%M%S"
LOG_FORMAT = "{0[utc_dt]}\t{0[local_dt]}\t{0[path]}\t{0[labels]}"

def dt_logstr(dt):
    return dt.strftime(LOG_DATETIME_FORMAT)

def dt_tolocal(dt):
    dt = dt.replace(tzinfo=tz.tzutc())
    return dt.astimezone(tz.tzlocal())

def dt_fromstr(date_string):
    dt = datetime.strptime(date_string,LOG_DATETIME_FORMAT)
    return dt

def dt_str(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S')

class Snaplog(object):
    @staticmethod
    def from_logstr(logstr):
        logstr = logstr.strip().strip("\t")
        if logstr == "": # blank line
            return None

        fields = logstr.split("\t")
        if len(fields) != 4: # invalid format
            return None 

        return Snaplog(fields[2],dt_fromstr(fields[0]),fields[3].split(","))

    @staticmethod
    def now():
        return datetime.utcnow()

    def __init__(self,path,dt=None,labels=[]):
        self.path = path
        self.labels = set(labels)
        self.dt = datetime.utcnow() if dt == None else dt

    def __str__(self):
        args = {
            "utc_dt" : self.dt.strftime(LOG_DATETIME_FORMAT),
            "local_dt" : dt_str(dt_tolocal(self.dt)),
            "path" : self.path,
            "labels" : ",".join(self.labels),
        }
        return LOG_FORMAT.format(args)

class Snaplogs(object):
    def __init__(self,filename=None):
        if filename != None:
            self.read(filename)
        else:
            self.logs = []

    def read(self,filename):
        self.logs = []
        
        if not os.path.exists(filename):
            return 
        try:
            with open(filename,"r") as fp:
                for line in fp:
                    log = Snaplog.from_logstr(line.strip())
                    if log != None : self.logs += [log]
        except IOError:
            print("[Error] Can't open or create SnapLog file {0}".format(filename))
            sys.exit(1)

    def write(self,filename):
        with open(filename,"w") as fp:
            for log in self.logs:
                fp.write(str(log)+"\n")

    def sort(self):
        self.logs.sort(key=lambda l : l.dt)

    def add(self,snaplog):
        self.logs += [snaplog]
        self.sort()

    def remove(self,snaplog):
        return self.logs.remove(snaplog)

    def count(self,label=None):
        return len(self.get(label))

    def get(self,label=None):
        out = []
        if label == "":
            return self.logs
        elif label == None:
            for log in self.logs:
                if len(log.labels) == 0:
                    out += [log]
        else :
            for log in self.logs:
                if label in log.labels:
                    out += [log]
        return out

    def get_latest(self,label=None):
        logs = self.get(label)
        length = len(logs)
        return logs[length-1] if length > 0 else None
