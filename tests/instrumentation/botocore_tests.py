import boto3
import mock

import opbeat
import opbeat.instrumentation.control
from opbeat.instrumentation.packages.botocore import BotocoreInstrumentation
from tests.helpers import get_tempstoreclient
from tests.utils.compat import TestCase


class InstrumentBotocoreTest(TestCase):
    def setUp(self):
        self.client = get_tempstoreclient()
        opbeat.instrumentation.control.instrument()

    @mock.patch("botocore.endpoint.Endpoint.make_request")
    def test_botocore_instrumentation(self, mock_make_request):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_make_request.return_value = (mock_response, {})

        self.client.begin_transaction("transaction.test")
        session = boto3.Session(aws_access_key_id='foo',
                                aws_secret_access_key='bar',
                                region_name='us-west-2')
        ec2 = session.client('ec2')
        ec2.describe_instances()
        self.client.end_transaction("MyView")

        _, traces = self.client.instrumentation_store.get_all()
        trace = [t for t in traces if t['kind'] == 'ext.http.aws'][0]
        self.assertIn('ec2:DescribeInstances', map(lambda x: x['signature'], traces))
        self.assertEqual(trace['signature'], 'ec2:DescribeInstances')
        self.assertEqual(trace['extra']['service'], 'ec2')
        self.assertEqual(trace['extra']['region'], 'us-west-2')

    def test_nonstandard_endpoint_url(self):
        instrument = BotocoreInstrumentation()
        self.client.begin_transaction('test')
        module, method = BotocoreInstrumentation.instrument_list[0]
        instance = mock.Mock(_endpoint=mock.Mock(host='https://example'))
        instrument.call(module, method, lambda *args, **kwargs: None, instance,
                        ('DescribeInstances',), {})
        self.client.end_transaction('test', 'test')
        _, traces = self.client.instrumentation_store.get_all()

        trace = [t for t in traces if t['kind'] == 'ext.http.aws'][0]
        self.assertEqual(trace['signature'], 'example:DescribeInstances')
        self.assertEqual(trace['extra']['service'], 'example')
        self.assertIsNone(trace['extra']['region'])
