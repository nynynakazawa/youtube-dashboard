import pymysql
from typing import Optional
from contextlib import contextmanager

from common.logger import get_logger
from constants.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

logger = get_logger(__name__)


@contextmanager
def get_db_connection():
    connection = None
    try:
        logger.debug("Connecting to database", extra={"host": DB_HOST, "database": DB_NAME})
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )
        logger.debug("Database connection established")
        yield connection
        connection.commit()
        logger.debug("Database transaction committed")
    except Exception as e:
        logger.error("Database error occurred", extra={"error": str(e), "error_type": type(e).__name__}, exc_info=True)
        if connection:
            connection.rollback()
            logger.debug("Database transaction rolled back")
        raise
    finally:
        if connection:
            connection.close()
            logger.debug("Database connection closed")

