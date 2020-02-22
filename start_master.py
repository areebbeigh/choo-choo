from config import MASTER_HOST
from master import create_master

server = create_master('', 8080)
server.serve_forever()