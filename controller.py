import sys

from config import MASTER_HOST, MASTER_PORT
from helpers import communicate
PASSWORD = '123456'

def fetch_stats():
    response = communicate.send_command(MASTER_HOST,
                    MASTER_PORT,
                    'CONTROLLER_STATS',
                    {'password': PASSWORD})
    print(response)

def send_start():
    response = communicate.send_command(MASTER_HOST, 
                    MASTER_PORT, 
                    'CONTROLLER_START', 
                    {'password': PASSWORD})
    
    if response != 'OK':
        print('Failed to start animation:', response)
        return
    print('Animation started.')

def print_cli(options):
    for option, (description, _) in options.items():
        print(f'{option}: {description}')

def cli():
    options = {
        1: ('Fetch stats', fetch_stats),
        2: ('Start animation', send_start)
    }
    while True:
        print_cli(options)
        print()
        try:
            response = int(input('>> '))
            if response not in options:
                raise ValueError()
        except ValueError:
            print('Invalid response!')
            continue
        try:
            options[response][1]()
        except:
            print(sys.exc_info()[1])

cli()