import os
import time
from subprocess import Popen, PIPE

def print_ts(message):
    print("[%s] %s"%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), message))
def run(interval,packageName):
    print_ts("-"*100)
    print_ts("Starting every %s seconds."%interval)
    while True:
        try:
            # sleep for the remaining seconds of interval
            time_remaining = interval-time.time()%interval
            print_ts("Sleeping until %s (%s seconds)..."%((time.ctime(time.time()+time_remaining)), time_remaining))
            time.sleep(time_remaining)
            print_ts("-"*100)
            print_ts("Starting command.")
            # execute the command
            # get pid for packageName
            commandGetPid = "adb shell pidof -s %s"
            info = Popen(commandGetPid % packageName, stdin=PIPE,stdout=PIPE, shell=True).communicate()[0]
            infos=info.decode('utf-8').split('\\r\\n')
            print("%s pid is %s "%(packageName,infos[0]))
            # get fb for pid
            commandGetFb = "adb shell lsof -p %s "
            print(commandGetFb % infos[0])
            fd = Popen(commandGetFb % infos[0], stdin=PIPE,stdout=PIPE, shell=True).communicate()[0]
            print_ts("-"*50)
            print(fd.decode('utf-8').split('\\r\\n')[0])
        except Exception as  e:
            print(e)
if __name__=="__main__":
    interval = 30
    run(interval,"cn.nubia.neostore")