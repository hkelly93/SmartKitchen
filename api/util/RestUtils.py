import json
import os
import datetime
import psutil
import subprocess


class RestUtils:
    """
    @author harrisonkelly,brianday

    Utility functions for the REST api.
    """
    @staticmethod
    def find_elem(dic, propName, propValue):
        """
        look for element in dict
        :param dic: dict to look through
        :param propName: key to search
        :param propValue: value to match
        :return: index of dict with corresponding element
        """
        for i in xrange(len(dic)):
            if dic[i][propName] == propValue:
                return i

        return None

    @staticmethod
    def set_expiration(days=None):
        date = datetime.datetime.today()

        if days is None:
            adjust_date = datetime.timedelta(days=30)

        else:
            adjust_date = datetime.timedelta(days=days)

        date += adjust_date  # need to increment before changing to a string
        date = date.strftime("%m/%d/%Y")

        return date

    @staticmethod
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


