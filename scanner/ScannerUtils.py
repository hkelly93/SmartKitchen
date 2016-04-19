import subprocess
import os


def find_process(proc_name, kill=False):
    print 'checking for process'
    # only works if rest-api is running on same machine
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()

    for line in out.splitlines():
        a = [proc_name, 'defunct']  # to solve issue with killing a subprocess but thread that was running it still exists

        if all(x in line for x in a):
            return False

        elif proc_name in line:
            if kill:
                pid = int(line.split(None, 1)[0])
                os.kill(pid, 9)
            return True

    return False
