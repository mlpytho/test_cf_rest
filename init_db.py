from sqlalchemy import create_engine, MetaData
from sqlalchemy.engine.base import Engine

from app.settings import config
from app.db import limit, transfer

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

def create_tables(engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[limit, transfer])


def sample_data(engine: Engine):
    conn = engine.connect()
    conn.execute(limit.insert(), [
        {'country': 'RUS', 'currency': 'RUB', 'maxtransf': 10_000},
        {'country': 'RUS', 'currency': 'USD', 'maxtransf': 10_000},
        {'country': 'RUS', 'currency': 'EUR', 'maxtransf': 10_000},
        {'country': 'ABH', 'currency': 'RUB', 'maxtransf': 1_000},
        {'country': 'ABH', 'currency': 'USD', 'maxtransf': 1_000},
        {'country': 'AUS', 'currency': 'EUR', 'maxtransf': 100_000},
    ])

    conn.close()


if __name__ == "__main__":
    db_url = DSN.format(**config['postgres'])
    engine = create_engine(db_url)

    create_tables(engine)
    # sample_data(engine)