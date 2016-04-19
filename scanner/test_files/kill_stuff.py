import subprocess
import os
def find_process(proc_name, kill=False):
        # only works if rest-api is running on same machine
        p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
        out, err = p.communicate()

        for line in out.splitlines():
            if proc_name and 'defunct' in line:
                print line
                pid = int(line.split(None, 1)[0])
                if kill:
                    os.kill(pid, 9)
                return True

        return False

#done = True
#while done:
    #done = find_process('/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python timer.py', True)
done = find_process('barcode_scanner', False)