import unittest

from mem_nr_db import Query, QueryLogic, MemNRDB, Table, DBException


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
        db.create_table("test")
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
        db.create_table("tost")

        t = db['tost']
        row2 = t.insert({"__id__": 2})
        row1 = t.insert({"hello": "world"})
        row3 = t.insert({"world": "hello"})

        self.assertEqual(row1['__id__'], 1)
        self.assertEqual(row2['__id__'], 2)
        self.assertEqual(row3['__id__'], 3)

        with self.assertRaises(DBException):
            t.insert({"__id__": 3})





if __name__ == '__main__':
    unittest.main()
