import time,schedule

task_list = list()
write_list = []

def clean_task_list():
    global task_list 
    global write_list

    for i in range(len(task_list)):
        task_list[i] = None

    write_list = []

def schedule_loop(interval=1,scheduler=schedule.default_scheduler):
    while True:
        clean_task_list()
        scheduler.run_pending()

        # write snaplogs
        for need_write in write_list:
            need_write.logs.write(need_write.snaplog_file)

        time.sleep(interval)

def schedule_work(snapmang,labels,index):
    global task_list
    global write_list

    if task_list[index] == None:
        task_list[index] = snapmang.snapshot(labels,auto_write=False)
        write_list += [snapmang] # add to write_list
    else:
        for label in labels:
            task_list[index].labels.add(label)
        snapmang.limit_check()

def schedule_task(snapmang):
    global task_list

    if "schedule-time" in snapmang.configs: 
        schedule_time = snapmang.configs["schedule-time"]
        
        # add to task_list
        task_list += [None]
        index = len(task_list)-1
        
        # schedule 
        for unit in schedule_time:
            if unit in {"second","minute","hour","day"}:
                job = schedule.every(int(schedule_time[unit]))
                job.unit = unit+"s"
                
                if "schedule-labels" in snapmang.configs and\
                   unit in snapmang.configs["schedule-labels"]:
                    job.do(schedule_work,snapmang,
                           snapmang.configs["schedule-labels"][unit],index)
                else:
                    job.do(schedule_work,snapmang,["node"],index)
