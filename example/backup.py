#!/usr/bin/python

from catsnapshot.snapmang import SnapManager
import catsnapshot.snapschedule as snapsch

sm = SnapManager.from_json("example/config.json")
print sm.configs

# take the first snapshot
if sm.logs.count("") == 0 :
    sm.snapshot(["node"])

snapsch.schedule_task(sm)
snapsch.schedule_loop()
