import socket
import time
import threading
import sys
from collections import deque

from helpers import communicate
from helpers.logs import get_logger

logger = get_logger(__name__)

class DispatchError(Exception): pass


class Worker:
    def __init__(self, host, port, id, dummy=False):
        self.id = id
        self.host = host
        self.port = int(port)
        self.dead = False
        self.playing = False
        self.played = False
        self.dummy = dummy
    
    def __repr__(self):
        return '<Worker (%s) %s:%s>' % (self.id, self.host, self.port)

    def __eq__(self, other):
        return self.host == other.host and self.port == other.port
    
    def play_ascii(self):
        self.playing = True
        return communicate.send_command(self.host, self.port, 'PLAY')
    
    def mark_ended(self):
        self.playing = False
        self.played = True

    def ping(self):
        assert not self.dead
        return communicate.send_command(self.host, self.port, 'PING')
        
    @classmethod
    def get_dummy_worker(self):
        return Worker('', -1, -1, True)


class WorkerService:
    def __init__(self, server):
        self.server = server
        self.workers = {}
        self.worker_list = deque()
        self.ready = False

    def init_threads(self):
        logger.info('Initializing service threads...')
        assert not self.ready
        worker_checker = threading.Thread(target=self.check_workers, name='worker_checker')
        worker_checker.start()
        self.ready = True
        logger.info('Service threads initialized.')
        return [worker_checker]

    def remove_worker(self, worker):
        """
        Removes a worker from the pool.
        """
        logger.info('Removing worker %s from pool...' % worker)
        worker.dead = True
        try:
            self.worker_list.remove(worker)
        except ValueError:
            pass
        self.workers[worker.id] = Worker.get_dummy_worker()
        logger.info('%s workers in pool.' % len(self.worker_list))

    def check_workers(self):
        """
        * This method is meant to run on a new thread *
        Periodically pings all workers, removes the unresponsive ones.
        """
        logger.info('Running worker checker')
        passed = 0
        while not self.server.dead:
            time.sleep(1)
            passed += 1
            if passed % 10 == 0:
                logger.info('Worker queue: %r' % self.worker_list)
            for id, worker in list(self.workers.items()):
                if worker.dead:
                    self.remove_worker(worker)
                    continue
                if worker.dummy:
                    continue
                try:
                    res = worker.ping()
                    if res != 'PONG':
                        self.remove_worker(worker)
                except socket.error:
                    logger.error('Worker %s did not response to PING' % worker)
                    logger.error(sys.exc_info()[1], exc_info=True)
                    self.remove_worker(worker)

    def _add_worker(self, worker):
        self.workers[worker.id] = worker
        self.worker_list.append(worker)
        logger.info('Worker %s added to pool' % worker)
        return worker

    def register(self, host, port):
        """Add a new worker to the pool."""
        worker = Worker(host, port, len(self.workers))
        logger.info('New worker register request from %s' % worker)
        assert worker not in self.workers.values()
        assert not self.workers.get(worker.id, None)
        return self._add_worker(worker)
    
    def reuse_worker(self, worker):
        logger.info('Re-Adding worker %s to the pool' % worker)
        worker.dead = False
        worker.playing = False
        worker.played = False
        return self._add_worker(worker)

    def get_worker(self, worker_id):
        logger.info('%r, %r, %r' % (self.workers.get(worker_id), self.workers, self.worker_list))
        assert self.workers.get(worker_id), f'Worker with id {worker_id} does not exist'
        return self.workers[worker_id]

    def mark_started(self, worker_id):
        logger.info('Marking worker id %s as playing...' % worker_id)
        worker = self.get_worker(worker_id)
        if not worker.playing:
            logger.info('Worker %s was not playing. Playing now.' % worker)
            assert worker.play_ascii() == 'OK'
        assert worker.playing == True
    
    def mark_ended(self, worker_id):
        worker = self.get_worker(worker_id)
        worker.mark_ended()
        logger.info('Marked %s as ended.' % worker)
        # assert self.worker_list.popleft() == worker
    
    def start_worker(self, worker):
        logger.info('Playing worker %s' % worker)
        assert worker.play_ascii() == 'OK', 'worker %s did not response after play' % worker
        self.mark_started(worker.id)

    def start_next(self, worker_id):
        worker = self.get_worker(worker_id)
        logger.info('Attempting to start worker after %s' % worker)
        next_worker = None
        while True:
            if not self.worker_list:
                break
            next_worker = self.worker_list.popleft()
            if not (next_worker.playing or next_worker.dead):
                break
        if next_worker:
            logger.info('Starting next worker %s' % next_worker)
            self.start_worker(next_worker)
        else:
            logger.info('No worker to start. Animation ended.')
    
    def start(self):
        logger.info('Initiating animation...')
        if not (self.worker_list and self.workers):
            raise Exception('No workers to run')
        worker = None
        while True:
            worker = self.worker_list.popleft()
            if not worker.dead:
                break
        if not worker:
            raise Exception('No workers to run')
        logger.info('Starting with worker %s' % worker)
        self.start_worker(worker)
