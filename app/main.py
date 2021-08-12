from aiohttp import web

from app.settings import config
from app.routes import setup_routes
from app.db import close_pg, init_pg

def init():
    app = web.Application()
    app['config'] = config
    setup_routes(app)
    app.on_startup.append(init_pg)
    app.on_cleanup.append(close_pg)
    return app


if __name__ == "__main__":
    app = init()
    web.run_app(app)