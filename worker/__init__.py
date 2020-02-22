from .server import ThreadingTCPServer
from .handler import TestHandler

def create_worker(host, 
                port,
                master_host,
                master_port):
    return ThreadingTCPServer(master_host,
                            int(master_port),
                            (host, int(port)),
                            TestHandler)