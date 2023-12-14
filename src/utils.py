import json

from collections import namedtuple


# FIXME: change client to list foramt as it changes
def client():
    # Define the namedtuple type
    Client = namedtuple('Client', 'lat lon zone city path weight id')

    # Read received Json file
    with open('../data/jsonfile.txt', mode='r') as f:
        data = json.load(f)

    clients = [Client._make(item.values()) for item in data['Customers']]
    return clients
