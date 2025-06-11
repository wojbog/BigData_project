from cassandra.cluster import Cluster
import time


def set_up():
    KEYSPACE = "cinema"

    for _ in range(10):
        try:
            cluster = Cluster(contact_points=["cassandra", "cassandra2"], port=9042)
            session = cluster.connect()
            break
        except Exception as e:
            print("Waiting for Cassandra...", str(e))
            time.sleep(30)

    session.execute(
        f"""
    CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
    WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': '1' }}"""
    )
    session.set_keyspace(KEYSPACE)

    session.execute("DROP TABLE IF EXISTS reservation")
    session.execute("DROP TABLE IF EXISTS cancellation")

    session.execute(
        """
    CREATE TABLE IF NOT EXISTS reservation (
        seat_id INT,
        user TEXT,
        PRIMARY KEY (seat_id)
    )
    """
    )

    session.execute(
        """
    CREATE TABLE IF NOT EXISTS cancellation (
        seat_id INT,
        user TEXT,
        PRIMARY KEY (seat_id)
    )
    """
    )

    return session


session = set_up()
