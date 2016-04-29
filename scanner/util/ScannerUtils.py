import subprocess
import os


def find_process(proc_name, kill=False):
    """
    only works if rest-api is running on same machine
    :param proc_name: string of process to look for/kill
    :param kill: True if you want to kill this process
    :return: true if found a process with the given name
    """
    # print 'checking for process %s' % proc_name


    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()  # saves all output together until process ends

    for line in out.splitlines():
        a = [proc_name, 'defunct']  # to solve issue with killing a subprocess but thread that was running it still exists

        if all(x in line for x in a):
            # print 'found zombie'
            return False

        elif proc_name in line:
            if kill:
                pid = int(line.split(None, 1)[0])
                os.kill(pid, 9)
                # print 'killing %s' % line
            #else:
                # print 'found: %s' % line
            return True

    return False
