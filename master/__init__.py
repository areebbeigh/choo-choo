import logging

from .server import ThreadingTCPServer
from .handler import Handler


def create_master(host, port):
    server = ThreadingTCPServer((host, int(port)), Handler)
    return server