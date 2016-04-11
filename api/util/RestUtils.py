import json
import datetime


class RestUtils:
    """
    @author harrisonkelly,brianday

    Utility functions for the REST api.
    """
    '''
    @staticmethod
    def generateInventoryEntry(barcode, addedDate, expirationDate):
        """
        Generates a JSON entry for the inventory.
        """
        entry = ""

        if (barcode != "" and addedDate != ""):
            entry = "    \"barcode\": \"" + barcode + "\",\n"
            entry += "    \"expirationdate\": \"" + expirationDate + "\",\n"
            entry += "    \"added\": \"" + addedDate + "\"\n}]"

            return entry
    '''

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
