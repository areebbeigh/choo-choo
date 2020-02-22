from helpers.parsing import urlencode

import socket

sep = b'\x00'

def new_connection(host, port, timeout=5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect((host, port))
    return s

def receive_data_from(socket, buff_size=1024):
    """
    Makes sure all the data is received in <data_length>\x00<data> format. Raises an 
    error if data is received in an invalid format and simply returns b'' if empty 
    data is received in the first buffer
    """
    buff = []
    length_received = 0
    data = socket.recv(1024)
    if not data:
        return data
    x = data.find(sep)
    # print('initial recv:', data, x)
    try:
        length_expected = int(data[:x])
    except ValueError:
        raise ValueError('Invalid incoming data format. Expected <data_length>\x00<data>')
    d = data[x + 1:]
    while True:
        # print('current buffer:', buff)
        buff.append(d)
        length_received += len(d)
        if length_received >= length_expected:
            break
        d = socket.recv(1024)
    return b''.join(buff)

def send_data_from(socket, data, skip_response=False):
    """Sends given data as <data_length>\x00<data> via socket.sendall."""
    try:
        if not isinstance(data, bytes):
            data = bytes(data, 'utf-8')
        msg = bytes(str(len(data)), 'utf-8') + sep + data
        socket.sendall(msg)
        if not skip_response:
            return receive_data_from(socket).decode()
    except:
        raise
    finally:
        socket.close()

def send_data(host, port, data, skip_response=False, timeout=5):
    """Creates a new socket to given address and sends the data."""
    s = new_connection(host, port, timeout)
    return send_data_from(s, data, skip_response)

def send_command(host, port, command, data=None, skip_response=False, timeout=5):
    """
    Creates a new socket to the given address and sends the 
    dictionary format data.
    """
    text = '%s ' % command
    if data:
        text += urlencode(data)
    return send_data(host, port, text, skip_response, timeout)