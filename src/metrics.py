from collections import defaultdict
import os
from sqlalchemy import select, text
from database import enable_rls, engine, readings, reset_db, sensors, set_store, seed


def get_time(result):
    return float(
        result[-1][0].lower().replace("execution time: ", "").replace(" ms", "")
    )


def get_times(query, store_id=None):
    times = []
    with engine.connect() as conn:
        if store_id is not None:
            set_store(conn, store_id)

        for _ in range(33):
            time = get_time(conn.execute(text("EXPLAIN ANALYZE " + query)).fetchall())
            times.append(time)

    return times


def get_plan(query, store_id=None):
    with engine.connect() as conn:
        if store_id is not None:
            set_store(conn, store_id)

        return conn.execute(text("EXPLAIN ANALYZE " + query)).fetchall()


"""
Queries:
Get all readings for the current tenant
Get all readings for the current tenant, but only for sensors of type 1 or 2
Get all readings joined with the sensor table for the current tenant
Get all sensors for the current tenant
Get all sensor_types
"""


normal_queries = [
    (
        "WITH valid_sensors AS (SELECT id FROM sensor WHERE store_id = 1) "
        "SELECT * FROM reading "
        "WHERE sensor_id IN (select id from valid_sensors)"
    ),
    (
        "WITH valid_sensors AS (SELECT id FROM sensor WHERE store_id = 1 "
        "AND (sensor_type_id = 1 OR sensor_type_id = 2)) "
        "SELECT * FROM reading "
        "WHERE sensor_id IN (select id from valid_sensors)"
    ),
    "SELECT * FROM reading, sensor WHERE reading.sensor_id = sensor.id AND sensor.store_id = 1",
    "SELECT * FROM sensor WHERE sensor.store_id = 1",
    "SELECT * FROM sensor_type",
]


def measure_normal():
    print("Normal")
    reset_db()
    seed()

    for query in normal_queries:
        yield query, get_times(query)


rls_queries = [
        "SELECT * FROM reading",
        (
            "WITH valid_sensors AS (SELECT id FROM sensor WHERE sensor_type_id = 1 OR sensor_type_id = 2) "
            "SELECT * FROM reading "
            "WHERE sensor_id IN (select id from valid_sensors)"
        ),
        "SELECT * FROM reading, sensor WHERE reading.sensor_id = sensor.id",
        "SELECT * FROM sensor",
        "SELECT * FROM sensor_type",
    ]


def measure_rls():
    print("RLS")
    reset_db()
    seed()
    enable_rls()

    for query in rls_queries:
        yield query, get_times(query, store_id=2)


if __name__ == "__main__":
    values_normal = defaultdict(list)
    values_rls = defaultdict(list)

    for query, values in measure_normal():
        values_normal[query] += values

    for query, values in measure_rls():
        values_rls[query] += values

    for query, values in measure_normal():
        values_normal[query] += values

    for query, values in measure_rls():
        values_rls[query] += values

    for query, values in measure_normal():
        values_normal[query] += values

    for query, values in measure_rls():
        values_rls[query] += values

    with open(f"{os.environ['DB_ENGINE']}.txt", "w") as f:
        for query, values in values_normal.items():
            f.write(f"{len(values)}\t{sum(values) / len(values)}\t{query}\n")

        f.write("\n")

        for query, values in values_rls.items():
            f.write(f"{len(values)}\t{sum(values) / len(values)}\t{query}\n")

        f.write("\n")

        reset_db()
        seed()
        for query in normal_queries:
            plan = get_plan(query, 2)
            for e in plan:
                f.write(f"{e[0]}\n")
            f.write("\n")
        
        reset_db()
        seed()
        enable_rls()
        for query in rls_queries:
            plan = get_plan(query, 2)
            for e in plan:
                f.write(f"{e[0]}\n")
            f.write("\n")

# with engine.connect() as conn:
#     set_store(conn, 2)
#     print('\n'.join(e[0] for e in conn.execute(text("EXPLAIN ANALYZE " + query)).fetchall()))
#     print(len(conn.execute(text(query)).fetchall()))
#     print()

# with engine.connect() as conn:
#     print('\n'.join(e[0] for e in conn.execute(text("EXPLAIN ANALYZE " + query)).fetchall()))
#     print(len(conn.execute(text(query)).fetchall()))
#     print()
