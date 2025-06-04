from cassandra.cluster import Cluster
import unittest


def create():
    cluster = Cluster(
        contact_points=['127.0.0.1', '127.0.0.2'],
        port=9042
    )

    session = cluster.connect('nicks')

    query1 = "create table if not exists nicks_t (name text, nodeId int, primary key (nodeId));"
    query3 = "Select * from nicks;"

    pre_query_insert = session.prepare("Insert into nicks_t (name, nodeId) values ('Stefan', ?);")

    session.execute(query1)
    # execute query


    for i in range(100):
        session.execute(pre_query_insert, [i])

# create()

class CassandraTest(unittest.TestCase):
    def setUp(self):
        self.cluster = Cluster(
            contact_points=['127.0.0.1', '127.0.0.2'],
            port=9042
        )
        self.session = self.cluster.connect('nicks')
        self.query3 = "Select * from nicks_t;"

    def test_insert(self):
        rows = self.session.execute(self.query3)
        i = 0
        for row in rows:
            i += 1
        self.assertEqual(i,100)

    
    def test_create_table(self):
        rows = self.session.execute(self.query3)
        self.assertTrue(rows)