from aiohttp.web_app import Application
from app.views import (
    all_limits, 
    get_limit, 
    add_limit, 
    update_limit, 
    delete_limit,
    add_transfer,
)

def setup_routes(app: Application):
    app.router.add_get('/limits', all_limits)
    app.router.add_post('/limit', add_limit)
    app.router.add_get('/limit/{id}', get_limit)
    app.router.add_put('/limit/{id}', update_limit)
    app.router.add_delete('/limit/{id}', delete_limit)

    app.router.add_post('/transfer', add_transfer)
