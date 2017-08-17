from elasticapm.base import Client
from elasticapm.middleware import ElasticAPM


def opbeat_filter_factory(app, global_conf, **kwargs):
    client = Client(**kwargs)
    return ElasticAPM(app, client)
