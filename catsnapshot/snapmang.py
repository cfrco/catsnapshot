from .rsync import Rsync
from . import snaplog
from .snaplog import dt_tolocal as dt2lo
import shutil
import json

AUTO_LABELS = {
    "hour" : lambda l,n : dt2lo(l.dt).date() == dt2lo(n.dt).date() and\
                          dt2lo(l.dt).hour == dt2lo(n.dt).hour,
    "day" : lambda l,n : dt2lo(l.dt).date() == dt2lo(n.dt).date(),
    "week" : lambda l,n : dt2lo(l.dt).isocalendar()[:2] == dt2lo(n.dt).isocalendar()[:2],
    "month" : lambda l,n : dt2lo(l.dt).year == dt2lo(n.dt).year and\
                           dt2lo(l.dt).month == dt2lo(n.dt).month,
}
DEFAULT_AUTO_LABELS = ["day","hour"]

class SnapManager(object):
    @staticmethod
    def from_json(filename):
        configs = json.load(open(filename,"r"))

        return SnapManager(configs["snaplog_file"],
                           configs["source_path"],
                           configs["backup_path"],
                           configs["limits"] if "limits" in configs else {},
                           configs["auto_labels"] if "auto_labels" in configs else None,
                           configs)
        
    # TODO : better __init__ function
    def __init__(self,snaplog_file,source_path,backup_path,limits,auto_labels=None,configs={}):
        self.snaplog_file = snaplog_file
        self.source_path = source_path if isinstance(source_path,list) else [source_path]
        self.backup_path = backup_path
        self.logs = snaplog.Snaplogs(self.snaplog_file)

        self.limits = limits
        self.configs = configs

        if auto_labels== None:
            self.auto_labels = set(DEFAULT_AUTO_LABELS)
        else:
            self.auto_labels = set(auto_labels)

        # configs:check-path 
        if "check-path" in self.configs:
            check_path = self.configs["check-path"]
            if isinstance(check_path,list):
                self.check_path = check_path
            else:
                self.check_path = [check_path]
        else:
            self.check_path = None

    def snapshot(self,labels=["node"],auto_write=True):
        prev = self.logs.get_latest("")
        prev_path = prev.path if prev!=None else None
        dt = snaplog.Snaplog.now()
        path = self.backup_path + snaplog.dt_logstr(dt)
        
        for sp in self.source_path:
            r = Rsync(sp,path,link_dest=prev_path)
            print r.cmd
            r.execute()
        
        log = snaplog.Snaplog(path,dt,labels)
        self.auto_label(log)
        self.logs.add(log)
        print log

        self.limit_check()
        if auto_write: self.logs.write(self.snaplog_file)
        return log

    def limit_check(self): 
        """ check limits after take a snapshot """
        for k,v in self.limits.items():
            if self.logs.count(k) > v:
                removed_log = self.logs.get(k)[0]
                removed_log.labels.remove(k)

                if self.remove(removed_log,check_label=True):
                    print "Remove : "+removed_log.path

    def remove(self,log,check_label=False,rmtree=True):
        """ when check_label and log.labels is not empty ,do nothing """
        if check_label and len(log.labels) != 0: 
            return False

        self.logs.remove(log)
        if rmtree:
            shutil.rmtree(log.path)
        return True

    def auto_label(self,log):
        """ label a log automatically with pre-defined condition """
        for label,autolabel in AUTO_LABELS.items():
            if not label in self.auto_labels:
                continue

            latest = self.logs.get_latest(label)

            # check whether the previous log with the same label should be remove
            if latest!=None and latest.dt<=log.dt and autolabel(latest,log):
                unlabel_log = latest
                unlabel_log.labels.remove(label)

                if self.remove(unlabel_log,check_label=True):
                    print "Remove : "+unlabel_log.path
            
            log.labels.add(label)
