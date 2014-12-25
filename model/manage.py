import postgres_db as pgdb
import time


pg_eng = pgdb.PG_ENGINE


def insert(eng, table, **kwargs):
    ins = table.insert().values(kwargs)
    result = eng.execute(ins)
    return result
