import sys
from socketserver import ThreadingMixIn, TCPServer

from .runner import WorkerService
from helpers.logs import get_logger

logger = get_logger(__name__)


class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    dead = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker_service = WorkerService(self)
    
    def serve_forever(self):
        try:
            threads = self.worker_service.init_threads()
            super().serve_forever()
        except BaseException:
            logger.error(sys.exc_info()[1], exc_info=True)
            self.dead = True
            # TODO: WorkerService should be cleaning its own mess.
            for t in threads:
                t.join()