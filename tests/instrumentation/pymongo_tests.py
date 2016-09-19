import os

import mock
import datetime
import json

import opbeat
import opbeat.instrumentation.control
from opbeat.traces import trace
from pymongo import MongoClient
from tests.helpers import get_tempstoreclient
from tests.utils.compat import TestCase


class InstrumentPyMongoTest(TestCase):
    def setUp(self):
        self.client = get_tempstoreclient()
        opbeat.instrumentation.control.instrument()
        self.mongo = MongoClient(
            os.environ.get('MONGODB_HOST', 'localhost'),
            int(os.environ.get('MONGODB_PORT', 27017)),
        )
        self.db = self.mongo.opbeat_test

    def tearDown(self):
        self.mongo.drop_database('opbeat_test')

    def test_collection_count(self):
        blogpost = {'author': 'Tom', 'text': 'Foo',
                    'date': datetime.datetime.utcnow()}
        self.db.blogposts.insert_one(blogpost)
        self.client.instrumentation_store.get_all()
        self.client.begin_transaction('transaction.test')
        with trace('test_mongodb', 'test'):
            count = self.db.blogposts.count()
            self.assertEqual(count, 1)
        self.client.end_transaction('transaction.test')
        transactions, traces = self.client.instrumentation_store.get_all()
        self.assertEqual(traces[0]['kind'], 'db.pymongo.query')
        self.assertEqual(traces[0]['signature'], 'blogposts.count')

    def test_collection_insert_one(self):
        blogpost = {'author': 'Tom', 'text': 'Foo',
                    'date': datetime.datetime.utcnow()}
        self.client.begin_transaction('transaction.test')
        with trace('test_mongodb', 'test'):
            r = self.db.blogposts.insert_one(blogpost)
            self.assertIsNotNone(r.inserted_id)
        self.client.end_transaction('transaction.test')
        transactions, traces = self.client.instrumentation_store.get_all()
        self.assertEqual(traces[1]['kind'], 'db.pymongo.query')
        self.assertEqual(traces[1]['signature'], 'blogposts.insert_one')

    def test_collection_insert_many(self):
        blogpost = {'author': 'Tom', 'text': 'Foo',
                    'date': datetime.datetime.utcnow()}
        self.client.begin_transaction('transaction.test')
        r = self.db.blogposts.insert_many([blogpost])
        self.assertEqual(len(r.inserted_ids), 1)
        self.client.end_transaction('transaction.test')
        transactions, traces = self.client.instrumentation_store.get_all()

        self.assertEqual(traces[0]['kind'], 'db.pymongo.query')
        self.assertEqual(traces[0]['signature'], 'blogposts.insert_many')

    def test_collection_delete_many(self):
        blogpost = {'author': 'Tom', 'text': 'Foo',
                    'date': datetime.datetime.utcnow()}
        self.client.begin_transaction('transaction.test')
        self.db.blogposts.insert_many([blogpost])
        r = self.db.blogposts.delete_many({'author': 'Tom'})
        self.assertEqual(r.deleted_count, 1)
        self.client.end_transaction('transaction.test')
        transactions, traces = self.client.instrumentation_store.get_all()
        self.assertEqual(traces[-1]['kind'], 'db.pymongo.query')
        self.assertEqual(traces[-1]['signature'], 'blogposts.delete_many')

    def test_collection_delete_one(self):
        blogpost = {'author': 'Tom', 'text': 'Foo',
                    'date': datetime.datetime.utcnow()}
        self.client.begin_transaction('transaction.test')
        self.db.blogposts.insert_many([blogpost])
        r = self.db.blogposts.delete_one({'author': 'Tom'})
        self.assertEqual(r.deleted_count, 1)
        self.client.end_transaction('transaction.test')
        transactions, traces = self.client.instrumentation_store.get_all()
        self.assertEqual(traces[-1]['kind'], 'db.pymongo.query')
        self.assertEqual(traces[-1]['signature'], 'blogposts.delete_one')
