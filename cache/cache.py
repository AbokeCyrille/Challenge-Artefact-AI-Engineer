from functools import lru_cache
from database.sql_executor import execute_sql

@lru_cache(maxsize=128)
def cached_sql(sql, params):
    return execute_sql(sql, params)
