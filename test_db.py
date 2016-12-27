import unittest

from mem_nr_db import Query, QueryLogic, MemNRDB, Table, DBException, Row, DBTypeError


class TestDB(unittest.TestCase):

    def test_filter_comp(self):
        q = Query("test") == 10  # type: Query
        self.assertIsInstance(q, Query)
        ch = q._check

        self.assertTrue(ch({"test": 10}))
        self.assertFalse(ch({"test": 15}))
        self.assertFalse(ch({"test": None}))
        self.assertTrue(ch({"test": 10.}))
        self.assertFalse(ch({"test": []}))
        self.assertFalse(ch({"test": "10"}))
        self.assertFalse(ch({"test": True}))
        self.assertFalse(ch({12: 10}))
        self.assertFalse(ch({"test_test": 10}))
        self.assertFalse(ch({}))

        q = Query(12) == True  # type: Query
        self.assertIsInstance(q, Query)
        ch = q._check

        self.assertTrue(ch({12: True}))
        self.assertFalse(ch({12: 10}))
        self.assertFalse(ch({12: 15}))
        self.assertFalse(ch({12: None}))
        self.assertFalse(ch({12: 10.}))
        self.assertFalse(ch({12: []}))
        self.assertFalse(ch({12: False}))
        self.assertFalse(ch({12: "10"}))
        self.assertFalse(ch({12: 10}))
        self.assertFalse(ch({"12": True}))
        self.assertFalse(ch({}))

        q = Query("a") < 10  # type: Query
        self.assertIsInstance(q, Query)
        ch = q._check

        self.assertTrue(ch({"a": 5}))
        self.assertFalse(ch({"a": 10}))
        self.assertFalse(ch({"a": 15}))

    def test_filter_logic(self):
        q = (Query("a") < 10) & (Query("b") >= 20)  # type: QueryLogic
        self.assertIsInstance(q, QueryLogic)
        ch = q._check

        self.assertTrue(ch({"a": 0, "b": 30}))
        self.assertFalse(ch({"a": 0, "b": 10}))
        self.assertFalse(ch({"a": 20, "b": 30}))
        self.assertFalse(ch({"a": 20, "b": 10}))
        self.assertTrue(ch({"a": 0, "b": 20}))

        self.assertFalse(ch({"b": 30}))
        self.assertFalse(ch({"a": 0}))
        self.assertFalse(ch({}))
        self.assertFalse(ch({"a": 0, "b": None}))

        q = (Query("a") < 10) | (Query("b") >= 20)  # type: QueryLogic
        self.assertIsInstance(q, QueryLogic)
        ch = q._check

        self.assertTrue(ch({"a": 0, "b": 30}))
        self.assertTrue(ch({"a": 0, "b": 10}))
        self.assertTrue(ch({"a": 20, "b": 30}))
        self.assertFalse(ch({"a": 20, "b": 10}))
        self.assertTrue(ch({"a": 0, "b": 20}))

        self.assertTrue(ch({"b": 30}))
        self.assertTrue(ch({"a": 0}))
        self.assertFalse(ch({}))
        self.assertTrue(ch({"a": 0, "b": None}))

    def test_db_query(self):
        db = MemNRDB()
        db.init_table("test")
        self.assertIsInstance(db['test'], Table)

        with self.assertRaises(DBException):
            t = db['tost']

        t = db['test']
        t.insert({"a": 5, "b": 10})
        t.insert({"a": 10, "b": 10})
        t.insert({"a": 20, "b": 10})
        t.insert({"a": 5, "b": 20})
        t.insert({"a": 10, "b": 20})
        t.insert({"a": 20, "b": 20})
        t.insert({"a": 5, "b": 25})
        t.insert({"a": 10, "b": 25})
        t.insert({"a": 20, "b": 25})

        data = list(t.query((Query("a") < 15) & (Query("b") > 15)).all())
        self.assertEqual(len(data), 4)
        for r in data:
            self.assertTrue((r['a'] < 15) and (r['b'] > 15))

    def test_db_index(self):
        db = MemNRDB()
        db.init_table("tost")

        t = db['tost']
        row2 = t.insert({"id": 2})
        row1 = t.insert({"hello": "world"})
        row3 = t.insert({"world": "hello"})

        self.assertEqual(row1['id'], 1)
        self.assertEqual(row2['id'], 2)
        self.assertEqual(row3['id'], 3)

        with self.assertRaises(DBException):
            t.insert({"id": 3})

    def test_update(self):
        db = MemNRDB()
        db.init_table("tost")

        t = db['tost']
        row2 = t.insert({"id": 2})
        row1 = t.insert({"hello": "world", "zzz": "xxx"})
        row3 = t.insert({"world": "hello"})

        with self.assertRaises(DBException):
            t.update({"id": 4, "val": 123})

        t.update({"id": 1, "hello": "WORLD", "xxx": "zzz"})
        row = t.get(1)
        self.assertEqual(row['id'], 1)
        self.assertEqual(row['hello'], "WORLD")
        self.assertEqual(row['zzz'], "xxx")
        self.assertEqual(row['xxx'], "zzz")

    def test_row(self):
        db = MemNRDB()
        db.init_table("tost")

        t = db['tost']
        t.insert({
            "id": 2,
            "test": "value",
            (1, 2): (3, 4),
            12: 34
        })

        row = t.get(2, to_class=True)
        self.assertIsInstance(row, Row)
        self.assertEqual(row.id, 2)
        self.assertEqual(row.test, "value")
        self.assertEqual(row[12], 34)
        self.assertEqual(row[1, 2], (3, 4))
        self.assertIsInstance(row._raw_data, dict)

    def test_assert(self):
        db = MemNRDB()
        db.init_table("tost")

        t = db['tost']
        with self.assertRaises(DBTypeError):
            t.insert([])

    def test_serialize(self):
        db = MemNRDB()
        t = db.init_table("tost")

        t.insert({"a": 12})
        t.insert({"бля": 23})

        tt = db.init_table("test")

        tt.insert({"c": 34})
        tt.insert({"d": 45})

        db.serialize("test_file.json")

        new_db = MemNRDB.load("test_file.json")

        tt = new_db['test']
        t = new_db['tost']

        self.assertIsInstance(tt, Table)
        self.assertIsInstance(t, Table)

        r = t.get(1, to_class=True)
        r2 = t.get(2, to_class=True)

        rr = tt.get(2, to_class=True)

        self.assertEqual(r.a, 12)
        self.assertEqual(r2['бля'], 23)

        self.assertEqual(rr.d, 45)

        r3 = Row(t.insert({"test": 333}))

        self.assertEqual(r3.test, 333)


if __name__ == '__main__':
    unittest.main()
