import pytest
from http import HTTPStatus
from alembic.command import downgrade, upgrade
from alembic.config import Config
# from app.main import init
from app.main import init


@pytest.fixture(scope='module')
def migrate_db():
    cfg = Config("alembic.ini")
    downgrade(cfg, 'base')
    upgrade(cfg, 'head')


@pytest.fixture
async def api_client(aiohttp_client, migrate_db):
    api_app = init()
    client = await aiohttp_client(api_app)

    try:
        yield client
    finally:
        await client.close()


async def test_limits_1(api_client):
    resp = await api_client.get('/limits')
    assert resp.status == HTTPStatus.OK
    assert await resp.json() == []


async def test_add_limit_1(api_client):
    limit = {"country":"RUS", "currency":"RUB", "maxtransf":"10000"}
    resp = await api_client.post('/limit', json=limit)
    assert resp.status == HTTPStatus.OK


async def test_get_limit_1(api_client):
    resp = await api_client.get('/limit/1')
    assert resp.status == HTTPStatus.OK

    assert await resp.json() == {
                "id": 1,
                "country": "RUS",
                "currency": "RUB",
                "maxtransf": 10000
            }


async def test_update_limit_1(api_client):
    limit = {"country":"RUS", "currency":"RUB", "maxtransf":"10"}
    resp = await api_client.put('/limit/1', json=limit)
    assert resp.status == HTTPStatus.OK
    assert await resp.json() == { "update": '1' }


async def test_delete_limit_1(api_client):
    resp = await api_client.delete('/limit/1')
    assert resp.status == HTTPStatus.OK
    assert await resp.json() == { "deleted": '1' }


async def test_get_wrong_limit_1(api_client):
    resp = await api_client.get('/limit/1')
    assert resp.status == HTTPStatus.NOT_FOUND


async def test_add_limit_2(api_client):
    limit = {"country":"RUS", "currency":"EUR", "maxtransf":"10000"}
    resp = await api_client.post('/limit', json=limit)
    assert resp.status == HTTPStatus.OK


async def test_add_transfer_1(api_client):
    transf = {"client_id": 111, "country":"RUS", "currency":"EUR", "amount": "3003", "date":"2021-01-01 10:00:00"}
    resp = await api_client.post('/transfer', json=transf)
    print(await resp.text())
    assert resp.status == HTTPStatus.OK
    assert await resp.json() == { "id": 1 }


async def test_add_transfer_2(api_client):
    transf = {"client_id": 111, "country":"RUS", "currency":"EUR", "amount": "9003", "date":"2021-01-03 10:00:00"}
    resp = await api_client.post('/transfer', json=transf)
    assert resp.status == HTTPStatus.NOT_FOUND
    assert await resp.text() == "Limit is exceeded"

