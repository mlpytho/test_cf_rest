import aiopg.sa
from sqlalchemy import MetaData, Table, UniqueConstraint
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import func, select
from sqlalchemy.engine.base import Connection


__all__ = ['limit', 'transfer']

meta = MetaData()

limit = Table(
    'limit', meta,
    Column('id', Integer, primary_key=True),
    Column('country', String(3), nullable=False),
    Column('currency', String(3), nullable=False),
    Column('maxtransf', Integer, nullable=False),

    UniqueConstraint('country', 'currency', name='uix_1'),
)

transfer = Table(
    'transfer', meta,

    Column('id', Integer, primary_key=True),
    Column('client_id', Integer, nullable=False),
    Column('date', DateTime, nullable=False),
    Column('amount', Integer, nullable=False),
    Column('country', String(3), nullable=False),
    Column('currency', String(3), nullable=False),
)


class RecordNotFound(Exception):
    """Rec not found"""
class InsertError(Exception):
    """insert error"""
class UpdateError(Exception):
    """update error"""
class DeleteError(Exception):
    """delete error"""
class LimitReachedError(Exception):
    """limit was reached"""


async def init_pg(app):
    conf = app['config']['postgres']
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
    )
    app['db'] = engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()


async def get_limits(conn: Connection):
    result = await conn.execute(
        limit.select()
    )
    records = await result.fetchall()
    limits = [dict(l) for l in records]
    return limits


async def get_limit(conn: Connection, id):
    result = await conn.execute(
        limit.select().where(limit.c.id == id)
    )
    lim_rec = await result.first()
    if not lim_rec:
        raise RecordNotFound(f'limit with {id} not found')
    
    return lim_rec


async def add_limit(conn: Connection, lim):
    result = await conn.execute(
        limit.insert().values(
            {
                'country': lim['country'],
                'currency': lim['currency'],
                'maxtransf': lim['maxtransf'],
            }
        )
    )
    lim_rec = await result.first()
    if not lim_rec:
        raise InsertError(f'add limit error with {str(id)}')
    
    return lim_rec


async def update_limit(conn: Connection, id, lim):
    result = await conn.execute(
        limit.update().where(limit.c.id == id).values(
            lim
        )
    )
    if not result.rowcount:
        raise UpdateError(f"Record with id {id} not found")
    return result.rowcount


async def delete_limit(conn: Connection, id):
    result = await conn.execute(
        limit.delete().where(limit.c.id == id)
    )
    if not result.rowcount:
        raise DeleteError(f"Record with id {id} not found")
    return result.rowcount


async def add_transfer(conn: Connection, data):
    lim = await conn.execute(
        select(limit.c.maxtransf)
            .where(limit.c.country == data['country'])
            .where(limit.c.currency == data['currency'])
    )
    lim = await lim.fetchone()
    if not lim:
        raise InsertError(f'limit not found for {data["country"]} {data["currency"]}')

    result = await conn.execute(
        select(func.sum(transfer.c.amount))
            .where(transfer.c.client_id == data['client_id'])
            .where(transfer.c.country == data['country'])
            .where(transfer.c.currency == data['currency'])
            .where(func.to_char(transfer.c.date, 'YYYY-MM') == 
                    func.to_char(func.date(data['date']), 'YYYY-MM')
            )
    )
    rec = await result.first()
    sum_amount = rec[0] if rec[0] else 0
    if lim[0] <= sum_amount + int(data['amount']):
        raise LimitReachedError()
    
    res = await conn.execute(
        transfer.insert().values(data)
    )
    res = await res.first()
    return res[0]