from sqlalchemy import create_engine, insert
from sqlalchemy import Table, Column, Integer, MetaData, ForeignKey
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.sql import text

meta = MetaData()

engine = create_engine("postgresql://user:password@postgres:5432/db")

stores = Table(
    "store",
    meta,
    Column("id", Integer, primary_key=True),
)

sensor_types = Table(
    "sensor_type",
    meta,
    Column("id", Integer, primary_key=True),
)

sensors = Table(
    "sensor",
    meta,
    Column("id", Integer, primary_key=True),
    Column("store_id", Integer, ForeignKey("store.id"), nullable=False, index=True),
    Column("sensor_type_id", Integer, ForeignKey("sensor_type.id"), nullable=False),
)

readings = Table(
    "reading",
    meta,
    Column("id", Integer, primary_key=True),
    Column("sensor_id", Integer, ForeignKey("sensor.id"), nullable=False, index=True),
)


def reset_db():
    meta.drop_all(engine)
    meta.create_all(engine)

    with engine.connect() as conn:
        conn.execute(insert(stores).values(id=1))
        conn.execute(insert(stores).values(id=2))
        conn.execute(insert(sensor_types).values(id=1))
        conn.execute(insert(sensor_types).values(id=2))
        conn.execute(insert(sensors).values(id=1, store_id=1, sensor_type_id=1))
        conn.execute(insert(sensors).values(id=2, store_id=2, sensor_type_id=2))
        conn.execute(insert(readings).values(id=1, sensor_id=1))
        conn.execute(insert(readings).values(id=2, sensor_id=2))


def seed():
    with engine.connect() as conn:
        conn.execute(
            sensor_types.insert(), [{"id": 3 + i} for i in range(20)]
        )

        conn.execute(
            sensors.insert(), [{"id": 3 + i, "sensor_type_id": i % 20 + 1, "store_id": i % 2 + 1} for i in range(100)]
        )

        conn.execute(
            readings.insert(), [{"id": 3 + i, "sensor_id": i % 20 + 1} for i in range(10000)]
        )


def enable_rls():
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE reading ENABLE ROW LEVEL SECURITY"))
        conn.execute(text("ALTER TABLE reading FORCE ROW LEVEL SECURITY"))
        conn.execute(text("ALTER TABLE sensor ENABLE ROW LEVEL SECURITY"))
        conn.execute(text("ALTER TABLE sensor FORCE ROW LEVEL SECURITY"))

        try:
            conn.execute(text('ALTER ROLE "user" NOBYPASSRLS'))
            conn.execute(text('ALTER ROLE "user" NOSUPERUSER'))
        except ProgrammingError:
            pass

        conn.execute(text("DROP POLICY IF EXISTS store ON sensor"))
        conn.execute(text("DROP POLICY IF EXISTS store ON reading"))
        conn.execute(
            text(
                f"""CREATE POLICY store ON sensor 
                USING (store_id = current_setting('variables.store_id')::INTEGER) 
                WITH CHECK (store_id = current_setting('variables.store_id')::INTEGER)"""
            )
        )
        conn.execute(
            text(
                """CREATE POLICY store ON reading
                USING (sensor_id IN (SELECT id FROM sensor))
                WITH CHECK (sensor_id IN (SELECT id FROM sensor))"""
            )
        )


def set_store(connection, store_id):
    connection.execute(text(f"SET variables.store_id = {store_id}"))
