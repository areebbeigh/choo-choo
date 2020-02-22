import re
import urllib.parse
from urllib.parse import urlencode


class Request:
    def __init__(self, type, data):
        self.type = type
        self.data = data
        for k, v in data.items():
            data[k] = v[0]

    def __repr__(self):
        return f'Request<{self.type} {self.data}>'

def parse_command(data):
    command_re = re.compile(r'(\w+) ?(.*)')
    match = command_re.match(data)
    command_name = match.group(1)
    query = urllib.parse.parse_qs(match.group(2), keep_blank_values=True)
    return Request(command_name, query)

def parse_qs(data):
    query = urllib.parse.parse_qs(data, keep_blank_values=True)
    for k, v in query.items():
        query[k] = v[0]
    return query
    
