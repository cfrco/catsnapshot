#!/usr/bin/python27
import argparse
import os,sys,time
from catsnapshot.snapmang import SnapManager
from catsnapshot import snapschedule as snapsch


def main_init():
    parser = argparse.ArgumentParser(description="CatSnapshot CLI tool")
    parser.add_argument("-d",dest="daemon",action="store_true",help="daemonize")
    parser.add_argument("-s",dest="atstart",action="store_true",help="backup at start")
    parser.add_argument("config_files",metavar="C",type=str,nargs="+",
                        help="config files")

    return parser.parse_args()

def main():
    args = main_init()

    for config_file in args.config_files:
        try:
            sm = SnapManager.from_json(config_file)
        except IOError as e :
            print e.strerror + " : " + config_file
            continue

        # take the first snapshot (when there is no snapshot or with `-s` option)
        if (snapsch.schedule_check_path(sm) and sm.logs.count("") == 0) \
           or args.atstart:
            sm.snapshot(["node"])

        # schedule tasks
        snapsch.schedule_task(sm)
    
    if args.daemon:
        """ http://code.activestate.com/recipes/66012-fork-a-daemon-process-on-unix/ """
        # do the UNIX double-fork magic, see Stevens' "Advanced 
        # Programming in the UNIX Environment" for details (ISBN 0201563177)
        try: 
            if os.fork() > 0:
                sys.exit(0) # exit first parent
        except OSError, e: 
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/") 
        os.setsid() 
        os.umask(0077) # create files/dirs with permission 0700

        # do second fork
        try: 
            if os.fork() > 0:
                sys.exit(0) # exit from second parent
        except OSError, e: 
            sys.exit(1) 

        snapsch.schedule_loop()
    else :
        snapsch.schedule_loop()


if __name__ == "__main__":
    main()
