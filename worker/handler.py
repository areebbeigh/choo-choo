import os
import sys

from helpers import communicate
from helpers.parsing import parse_command, urlencode
from helpers.handler import BaseHandler
from helpers.logs import get_logger

from .player import AsciiPlayer

# TODO: periodically check if we're connected to the master
logger = get_logger(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ART_FILE = os.path.join(BASE_DIR, 'art.txt')


class TestHandler(BaseHandler):
    def handle(self):
        self.data = communicate.receive_data_from(self.request).decode()
        self.request_obj = parse_command(self.data)
        if self.request_obj.type != 'PING':
            logger.debug(self.data)
            logger.info('%s %s', self.request_obj.type, self.request_obj.data)
        handler = self.get_handler(self.request_obj.type)
        handler()
    
    def cmd_REGISTERED(self):
        self.server.worker_id = self.request_obj.data['id']

    def cmd_PLAY(self):
        with open(ART_FILE, 'r') as f:
            player = AsciiPlayer(f)
            player.start()
        communicate.send_command(*self.server.master_address, 'ENDED', 
            {'id': self.server.worker_id},
            skip_response=True)

    def cmd_PING(self):
        communicate.send_data_from(self.request, 'PONG', True)
