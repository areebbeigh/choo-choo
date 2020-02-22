import sys
from socketserver import ThreadingMixIn, TCPServer

from helpers import communicate
from helpers.logs import get_logger

logger = get_logger(__name__)


class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    dead = False
    def __init__(self,
        master_host,
        master_port,
        address,
        *args, 
        **kwargs):

        super().__init__(address, *args, **kwargs)
        self.host, self.port = address
        self.master_address = (master_host, master_port)
        self.register_to_master()

    def serve_forever(self):
        super().serve_forever()

    def register_to_master(self):
        logger.info('Registering worker to master %s' % str(self.master_address))
        response = communicate.send_command(
            *self.master_address, 
            'REGISTER',
            {
                'host': self.host,
                'port': self.port
            })
        logger.info('Got response: %s', response)
        assert response == 'OK', 'Could not register to master.'
        logger.info('Registered to master.')