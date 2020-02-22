import sys

from worker import create_worker
from config import MASTER_HOST, MASTER_PORT

port = 9000
if len(sys.argv) > 1:
    port = sys.argv[1]

while True:
    try:
        server = create_worker('', port, MASTER_HOST, MASTER_PORT)
    except OSError:
        print('Port', port, 'unavailable. Trying', port + 1)
        port += 1
        continue
    break
server.serve_forever()