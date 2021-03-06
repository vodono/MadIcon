import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
from PIL import Image

from tornado.options import define, options


define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
    """
    Create Tornado application with main index page and websocket handler
    for update of icon position.
    """
    def __init__(self):
        handlers = [(r"/", MainHandler), (r"/iconsocket", IconSocketHandler)]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        super(Application, self).__init__(handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    """
    Obtain icon size and render index page with actual coordinates and icon size.
    """
    def get(self):
        with Image.open(os.path.dirname(__file__)+'/static/tdo.png', 'r') as image:
            self.width, self.height = image.size

        self.render(
            "index.html",
            position_h=IconSocketHandler.position_h,
            position_v=IconSocketHandler.position_v,
            width=self.width,
            height=self.height,
        )


class IconSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    position_h = 0
    position_v = 0

    def open(self):
        IconSocketHandler.waiters.add(self)

    def on_close(self):
        IconSocketHandler.waiters.remove(self)

    @classmethod
    def send_updates(cls, forward_message):
        for waiter in cls.waiters:
            try:
                waiter.write_message(forward_message)
            except:
                print("Error sending message")

    def on_message(self, message):
        """
        On receiving of message with new coordinates save them and send to all
        waiters.
        """
        parsed = tornado.escape.json_decode(message)
        IconSocketHandler.position_v = parsed['position_v']
        IconSocketHandler.position_h = parsed['position_h']
        forward_message = {
            "position_v": IconSocketHandler.position_v,
            "position_h": IconSocketHandler.position_h,
        }
        IconSocketHandler.send_updates(forward_message)


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
