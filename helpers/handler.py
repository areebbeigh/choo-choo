from socketserver import BaseRequestHandler

from helpers.communicate import send_data_from


class BaseHandler(BaseRequestHandler):
    def fail(self, msg):
        send_data_from(self.request, msg, True)
        raise Exception(msg)

    def get_handler(self, name):
        cmd_name = 'cmd_' + name
        try:
            return getattr(self, cmd_name)
        except AttributeError:
            self.fail('Invalid command ' + cmd_name)