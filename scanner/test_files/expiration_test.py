import os.path
import datetime
import collections
import json


def expiration_date(barcode, days=None):
    """
    need to find the correct item to change
    without an index id this would find the first item with the same barcode in the inventory
    which may not be the desired effect
    :param barcode: string representation
    :param days: how many days till expiration
    :return:
    """

    date = set_expiration(days)
    try:
        with open('json/inventory.json', 'r') as json_file:
            data = json.load(json_file)  # Get the current inventory.
            json_file.close()

            index = find_elem(data, "barcode", barcode)

            if index is not None:
                data[index]['expiration'] = unicode(date)
                with open('json/inventory.json', 'w+') as json_file:
                    json_file.write(json.dumps(data))
                    json_file.close()
            else:
                print "nothing to update"

    except IOError:
        pass

    return ''


def set_expiration(days=None):
    date = datetime.datetime.today()

    if days is None:
        adjust_date = datetime.timedelta(days=30)

    else:
        adjust_date = datetime.timedelta(days=days)

    date += adjust_date  # need to increment before changing to a string
    #date = date.strftime("%m/%d/%Y")

    return date


def add_item(barcode, days_till_expire=None):
    """
    add item to the inventory
    will increment quantity of pre existing items
    :param barcode: string representation of barcode
    :param days_till_expire: defaults to None which will set it 30 days from today's date
    :return: nothing
    """

    added_date = datetime.datetime.today().strftime("%m/%d/%Y %H:%M:%S")
    expire_date = set_expiration(days_till_expire)

    # TODO add filelock
    try:
        with open('json/inventory.json', 'r') as json_file:
            data = json.load(json_file)
            json_file.close()

            index = find_elem(data, u"barcode", barcode)  # returns index if already exists

        # there already exists this barcode in the inventory
        if index is not None:
            data[index]['qty'] += 1
            data[index]["expiration"] = unicode(expire_date)
        else:
            # this order matters, layout will add in same order in json
            d = {u'barcode': unicode(barcode),
                 u'added': unicode(added_date),
                 u'expiration': unicode(expire_date),
                 u'qty': 1}

            data.append(d)

        # open up file again to write to it
        with open('json/inventory.json', 'w+') as json_file:
            json_file.write(json.dumps(data, encoding='utf-8'))
            json_file.close()

    except (IOError,KeyError):
        # TODO exception error here
        pass


def del_item(barcode):
    """
    remove the given item from inventory
    this really should be checking for some sort of unique identifier

    :param barcode: string representation
    :return:
    """
    try:
        with open('json/inventory.json', 'r') as json_file:
            data = json.load(json_file)  # Get the current inventory.
            json_file.close()

        index = find_elem(data, 'barcode', barcode)

        if index is not None:
            del data[index]
            with open('json/inventory.json', 'w+') as json_file:
                json_file.write(json.dumps(data))
                json_file.close()
            return True
        else:
            print 'nothing to delete'
            return False

    except (IOError, KeyError):
        print "file doesnt exist or keyerror"




def find_elem(arr, propName, propValue):
    for i in xrange(len(arr)):
        if arr[i][propName] == propValue:
            return i
    return None

#expiration_date("018018281", 180)
#add_item("018018281", 45)
#del_item(u'08748001')
#add_item("018018281")