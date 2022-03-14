from sqlalchemy import select
from database import engine, readings, sensors


def get_readings(conn):
    query = select(readings)
    return conn.execute(query).fetchall()


def get_readings_by_sensor_type(conn, sensor_type_id):
    query = select([readings, sensors])
    query = query.select_from(readings.join(sensors))
    query = query.where(sensors.c.sensor_type_id == sensor_type_id)
    return conn.execute(query).fetchall()
