import implementation_one
import implementation_two

from database import enable_rls, set_store, engine


if __name__ == "__main__":
    with engine.connect() as conn:
        assert implementation_one.get_readings(conn, 1) == [(1, 1, 1, 1, 1)]
        assert implementation_one.get_readings_by_sensor_type(conn, 1, 2) == []
        assert implementation_one.get_readings_by_sensor_type(conn, 2, 2) == [
            (2, 2, 2, 2, 2)
        ]

    enable_rls()

    with engine.connect() as conn:
        set_store(conn, 1)
        assert implementation_two.get_readings(conn) == [(1, 1)]
        assert implementation_two.get_readings_by_sensor_type(conn, 2) == []
        set_store(conn, 2)
        assert implementation_two.get_readings_by_sensor_type(conn, 2) == [
            (2, 2, 2, 2, 2)
        ]

    print("Success!")
