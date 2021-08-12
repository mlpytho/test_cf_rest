from aiohttp import web

from app import db

async def all_limits(request: web.Request):
    async with request.app['db'].acquire() as conn:
        limits = await db.get_limits(conn)
        return web.json_response(limits)


async def get_limit(request: web.Request):
    async with request.app['db'].acquire() as conn:
        lid = request.match_info['id']
        try:
            lim = await db.get_limit(conn, lid)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))
        return web.json_response(dict(lim))


async def add_limit(request: web.Request):
    async with request.app['db'].acquire() as conn:
        lim = await request.json()
        try:
            lim = await db.add_limit(conn, lim)
        except db.InsertError as e:
            raise web.HTTPNotFound(text=str(e))
        return web.json_response(dict(lim))


async def update_limit(request: web.Request):
    async with request.app['db'].acquire() as conn:
        lim = await request.json()
        lid = request.match_info['id']
        try:
            _ = await db.update_limit(conn, lid, lim)
        except db.UpdateError as e:
            raise web.HTTPNotFound(text=str(e))
        return web.json_response({"update": lid})


async def delete_limit(request: web.Request):
    async with request.app['db'].acquire() as conn:
        lid = request.match_info['id']
        try:
            _ = await db.delete_limit(conn, lid)
        except db.DeleteError as e:
            raise web.HTTPNotFound(text=str(e))
        return web.json_response({"deleted": lid})


async def add_transfer(request: web.Request):
    async with request.app['db'].acquire() as conn:
        data = await request.json()
        try:
            tid = await db.add_transfer(conn, data)
        except db.InsertError as e:
            raise web.HTTPNotFound(text=str(e))
        except db.LimitReachedError as e:
            raise web.HTTPNotFound(text="Limit is exceeded")
        return web.json_response({"id": tid})