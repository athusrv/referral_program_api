import os
from contextlib import contextmanager

from alembic import command, config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base

engine = create_engine(os.environ.get('DB_CNX', default='sqlite:///:memory:'), echo=False)
Entity = declarative_base()


def new_session():
    return Session(bind=engine)


def migrate():
    alembic_cfg = config.Config(os.path.normpath(os.path.join(os.path.dirname(__file__), '../alembic.ini')))
    command.upgrade(alembic_cfg, "head")


@contextmanager
def db_transaction():
    # provide a transactional scope around a series of operations
    session = new_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
