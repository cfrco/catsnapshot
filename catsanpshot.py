from rsync import Rsync
import snaplog
import shutil
import json

class SnapManager(object):
    @staticmethod
    def from_json(filename):
        configs = json.load(open(filename,"r"))

        return SnapManager(configs["log_file"],
                          configs["source_path"],
                          configs["backup_path"])
        

    def __init__(self,log_file,source_path,backup_path):
        self.log_file = log_file
        self.source_path = source_path
        self.backup_path = backup_path
        self.logs = snaplog.Snaplogs(self.log_file)

        self.limits = {
            "hour" : 4,
            "day" : 1,
            "week" : 4,
        }

    def snapshot(self):
        prev = self.logs.get_latest("")
        prev_path = prev.path if prev!=None else None
        dt = snaplog.Snaplog.now()
        path = self.backup_path + snaplog.dt_logstr(dt)
        print path
        
        r = Rsync(self.source_path,path,link_dest=prev_path)
        print r.cmd
        r.execute()
        
        log = snaplog.Snaplog(path,dt,["hour"])
        print log
        self.auto_label(log)
        self.logs.add(log)

        self.limit_check_after()
        self.logs.write(self.log_file)

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
        if self.logs.get_latest("day").dt.date == log.dt.date :
            unlabel_log = self.logs.get_latest("day")
            unlabel_log.labels.remove("day")
            self.delete_empty_lable(unlabel_log)
            log.labels.add("day")
        else :
            log.labels.add("day")

#sm = SnapManager("/tmp/backup/log","/tmp/target","/tmp/backup/")
sm = SnapManager.from_json("./config.example.json")
#sm.snapshot()
