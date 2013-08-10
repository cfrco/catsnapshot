from rsync import Rsync
import snaplog
import shutil
import json

AUTO_LABELS = {
    "day" : lambda l,n : l.dt.date() == n.dt.date(),
    "hour" : lambda l,n : l.dt.date() == n.dt.date() and\
                          l.dt.hour == n.dt.hour,
}
DEFAULT_AUTO_LABELS = ["day","hour"]

class SnapManager(object):
    @staticmethod
    def from_json(filename):
        configs = json.load(open(filename,"r"))

        return SnapManager(configs["snaplog_file"],
                           configs["source_path"],
                           configs["backup_path"],
                           configs["limits"],
                           configs["auto_labels"] if "auto_labels" in configs else None)
        
    def __init__(self,snaplog_file,source_path,backup_path,limits,auto_labels=None):
        self.snaplog_file = snaplog_file
        self.source_path = source_path
        self.backup_path = backup_path
        self.logs = snaplog.Snaplogs(self.snaplog_file)

        self.limits = limits

        if auto_labels== None :
            self.auto_labels = set(DEFAULT_AUTO_LABELS)
        else :
            self.auto_labels = set(auto_labels)

    def snapshot(self):
        prev = self.logs.get_latest("")
        prev_path = prev.path if prev!=None else None
        dt = snaplog.Snaplog.now()
        path = self.backup_path + snaplog.dt_logstr(dt)
        print path
        
        r = Rsync(self.source_path,path,link_dest=prev_path)
        print r.cmd
        r.execute()
        
        log = snaplog.Snaplog(path,dt,["node"])
        print log
        self.auto_label(log)
        self.logs.add(log)

        self.limit_check_after()
        self.logs.write(self.snaplog_file)

    def limit_check_after(self):
        for k,v in self.limits.items() :
            if self.logs.count(k) > v :
                removed_log = self.logs.get(k)[0]
                removed_log.labels.remove(k)

                self.delete_empty_label(removed_log)

    def delete_empty_label(self,log):
        if len(log.labels) == 0:
            print "Removing "+log.path
            shutil.rmtree(log.path)
            self.logs.remove(log)

    def auto_label(self,log):
        for label,autolabel in AUTO_LABELS.items() :
            if not label in self.auto_labels:
                continue

            latest = self.logs.get_latest(label)
            if latest!=None and autolabel(latest,log):
                unlabel_log = self.logs.get_latest(label)
                unlabel_log.labels.remove(label)
                self.delete_empty_label(unlabel_log)
                log.labels.add(label)
            else :
                log.labels.add(label)

#sm = SnapManager("/tmp/backup/log","/tmp/target","/tmp/backup/")
sm = SnapManager.from_json("./config.example.json")
sm.snapshot()
