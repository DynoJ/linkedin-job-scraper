import oracledb
from contextlib import contextmanager
from typing import Generator, Optional
from src.config.settings import oracle_config


class Database:
    _pool: Optional[oracledb.ConnectionPool] = None

    @classmethod
    def init_pool(cls, min_connections: int = 2, max_connections: int = 10) -> None:
        if cls._pool is None:
            cls._pool = oracledb.create_pool(
                user=oracle_config.user,
                password=oracle_config.password,
                dsn=oracle_config.dsn,
                min=min_connections,
                max=max_connections,
            )

    @classmethod
    def close_pool(cls) -> None:
        if cls._pool:
            cls._pool.close()
            cls._pool = None

    @classmethod
    @contextmanager
    def get_connection(cls) -> Generator[oracledb.Connection, None, None]:
        if cls._pool is None:
            cls.init_pool()
        connection = cls._pool.acquire()
        try:
            yield connection
        finally:
            cls._pool.release(connection)

    @classmethod
    @contextmanager
    def get_cursor(cls) -> Generator[oracledb.Cursor, None, None]:
        with cls.get_connection() as connection:
            cursor = connection.cursor()
            try:
                yield cursor
                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()