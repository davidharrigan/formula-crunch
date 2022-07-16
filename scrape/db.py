import os

import sqlalchemy


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def create_connection():
    filename = os.path.join(ROOT_DIR, '..', 'data', 'db.sqlite')
    print(f'sqlite:///{filename}')
    conn = sqlalchemy.create_engine(f'sqlite:///{filename}', echo=True)
    return conn
