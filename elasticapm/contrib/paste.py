from elasticapm.base import Client
from elasticapm.middleware import Opbeat


def opbeat_filter_factory(app, global_conf, **kwargs):
    client = Client(**kwargs)
    return Opbeat(app, client)
