from collections import namedtuple

from django.db import connection


def exec_query(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
    if sql.strip().startswith('--'):
        raw_header = sql.strip().split('\n')[0]
        name, _, header = raw_header.partition(':')
        named = namedtuple(name.replace('--', ''), header)
        return [named(*item) for item in rows]
    return rows