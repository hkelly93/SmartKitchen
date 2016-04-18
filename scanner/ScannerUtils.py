import subprocess
import os

def find_process(proc_name, kill=False):
    # only works if rest-api is running on same machine
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()

    for line in out.splitlines():
        if proc_name in line:
            pid = int(line.split(None, 1)[0])
            if kill:
                os.kill(pid, 9)
            return True

    return False
