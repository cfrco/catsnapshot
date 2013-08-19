import time,schedule,datetime
import signal,os,sys

task_list = list()
write_list = []
feqcheck_list = []

def clean_task_list():
    global task_list 
    global write_list

    for i in range(len(task_list)):
        task_list[i] = None

    write_list = []

class schedule_sig_handler(object):
    def __init__(self,status):
        self.status = status

    def handler_func(self,signum,frame):
        if self.status == "working":
            self.status = "exit"
        else:
            sys.exit(0)

def schedule_loop(interval=1,scheduler=schedule.default_scheduler):
    sch_sig = schedule_sig_handler("idle")

    # Set the signal handler
    sigint_dh = signal.signal(signal.SIGINT,sch_sig.handler_func)
    sigterm_dh = signal.signal(signal.SIGTERM,sch_sig.handler_func)

    while True:
        sch_sig.status = "working"
        clean_task_list()
        scheduler.run_pending()
        
        # write snaplogs
        for need_write in write_list:
            need_write.logs.write(need_write.snaplog_file)
        
        # feqcheck
        schedule_feqcheck_work()

        if sch_sig.status == "exit": sys.exit(0)
        else: sch_sig.status = "idle"
        time.sleep(interval)
    
    # Set signal handler to default handler
    signal.signal(signal.SIGINT,sigint_dh)
    signal.signal(signal.SIGTERM,sigterm_dh)

def schedule_check_path(snapmang):
    if snapmang.check_path:
        for path in snapmang.check_path:
            if not os.path.exists(path):
                return False
    return True
    
def schedule_rerun(job):
    """Run the job , but not reschedule it."""
    #logger.info('Running job %s', job)
    job.job_func()
    job.last_run = datetime.datetime.now() # refresh last_run

def schedule_feqcheck_work():
    global feqcheck_list

    for snapmang in feqcheck_list:
        if snapmang.latest_undone!=None and schedule_check_path(snapmang):
            schedule_rerun(snapmang.latest_undone)

def schedule_work(snapmang,labels,index,job):
    global task_list
    global write_list

    if schedule_check_path(snapmang) is False:
        snapmang.latest_undone = job
        return 

    if task_list[index] == None:
        task_list[index] = snapmang.snapshot(labels,auto_write=False)
        write_list += [snapmang] # add to write_list
    else:
        for label in labels:
            task_list[index].labels.add(label)
        snapmang.limit_check()

    snapmang.latest_undone = None

def schedule_task(snapmang):
    global task_list
    global feqcheck_list

    if "schedule-time" in snapmang.configs: 
        schedule_time = snapmang.configs["schedule-time"]
        
        # add to task_list
        task_list += [None]
        index = len(task_list)-1
        
        # init undone and add to feqcheck_list
        snapmang.latest_undone = None
        if "feqcheck" in snapmang.configs:
            if snapmang.configs["feqcheck"] == True:
                feqcheck_list += [snapmang]
        
        # schedule 
        for unit in schedule_time:
            if unit in {"second","minute","hour","day"}:
                job = schedule.every(int(schedule_time[unit]))
                job.unit = unit+"s"
                
                if "schedule-labels" in snapmang.configs and\
                   unit in snapmang.configs["schedule-labels"]:
                    job.do(schedule_work,snapmang,
                           snapmang.configs["schedule-labels"][unit],index,job)
                else:
                    job.do(schedule_work,snapmang,["node"],index,job)
