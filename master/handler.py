import time

from helpers.parsing import parse_command, urlencode
from helpers.communicate import receive_data_from, send_data_from, send_command
from helpers.handler import BaseHandler
from helpers.logs import get_logger

logger = get_logger(__name__)
PASSWORD = '123456' # super secure.


class Handler(BaseHandler):
    def handle(self):
        self.worker_service = self.server.worker_service
        self.data = receive_data_from(self.request).decode()
        logger.debug(self.data)
        self.request_obj = parse_command(self.data)
        logger.info('%s %s', self.request_obj.type, self.request_obj.data)
        if self.request_obj.data.get('id'):
            self.request_obj.data['id'] = int(self.request_obj.data['id'])
        handler = self.get_handler(self.request_obj.type)
        handler()
    
    def authenticate_controller(self):
        pw = self.request_obj.data['password']
        if pw == PASSWORD:
            logger.info('Controller authenticated.')
            return True
        send_data_from(self.request, 'Invalid authentication', True)
        raise Exception()

    def cmd_CONTROLLER_STATS(self):
        self.authenticate_controller()

    def cmd_CONTROLLER_START(self):
        self.authenticate_controller()
        try:
            self.worker_service.start()
        except:
            return send_data_from(self.request, 'Could not start animation', True)
        return send_data_from(self.request, 'OK')
    
    def cmd_STATUS(self):
        send_data_from(self.request, 'OK', True)

    def cmd_STARTED(self):
        self.worker_service.mark_started(self.request_obj.data['id'])

    def cmd_START_NEXT(self):
        self.worker_service.start_next(self.request_obj.data['id'])
    
    def cmd_ENDED(self):
        try:
            time.sleep(0.5)
            self.worker_service.start_next(self.request_obj.data['id'])
        except:
            pass
        finally:
            worker = self.worker_service.get_worker(self.request_obj.data['id'])
            self.worker_service.remove_worker(worker)
            self.worker_service.reuse_worker(worker)

    def cmd_REGISTER(self):
        host = self.request.getpeername()[0]
        port = self.request_obj.data['port']
        worker = self.worker_service.register(host, int(port))
        send_data_from(self.request, 'OK')
        send_command(worker.host, worker.port, 'REGISTERED', {
            'id': worker.id}, 
            skip_response=True)
        # send_command(worker.host, worker.port, 'PLAY', {}, skip_response=True)
