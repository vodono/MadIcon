# import logging
# import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
# import uuid

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
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
    def get(self):
        self.render(
            "index.html",
            position_h=IconSocketHandler.position_h,
            position_v=IconSocketHandler.position_v
        )


class IconSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    position_h = 0
    position_v = 0

    # def get_compression_options(self):
    #     # Non-None enables compression with default options.
    #     return {}

    def open(self):
        IconSocketHandler.waiters.add(self)

    def on_close(self):
        IconSocketHandler.waiters.remove(self)

    # @classmethod
    # def update_cache(cls, chat):
    #     cls.cache.append(chat)
    #     if len(cls.cache) > cls.cache_size:
    #         cls.cache = cls.cache[-cls.cache_size :]

    @classmethod
    def send_updates(cls, forward_message):
        # logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(forward_message)
            except:
                print("Error sending message")# logging.error("Error sending message", exc_info=True)

    def on_message(self, message):
        # logging.info("got message %r", message)
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
