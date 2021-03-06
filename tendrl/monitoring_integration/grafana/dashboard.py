import __builtin__
import os
import json
import traceback


from requests import get, post, put

from tendrl.monitoring_integration.grafana import utils
from tendrl.monitoring_integration.grafana import exceptions

HEADERS = {"Accept": "application/json",
           "Content-Type": "application/json"
           }


'''Create Dashboard'''


def _post_dashboard(dashboard_json):
    config = NS.conf
    if utils.port_open(config.grafana_port, config.grafana_host):
        upload_str = json.dumps(dashboard_json)
        resp = post("http://{}:{}/api/dashboards/"
                    "db".format(config.grafana_host,
                                config.grafana_port),
                    headers=HEADERS,
                    auth=config.credentials,
                    data=upload_str)
    else:
        raise exceptions.ConnectionFailedException

    return resp


def get_dashboard(dashboard_name):
    config = NS.conf
    if utils.port_open(config.grafana_port, config.grafana_host):
        resp = get("http://{}:{}/api/dashboards/"
                   "db/{}".format(config.grafana_host,
                                  config.grafana_port,
                                  dashboard_name),
                   auth=config.credentials)
    else:
        raise exceptions.ConnectionFailedException
    return resp.json()


def get_all_dashboards():
    config = NS.conf
    if utils.port_open(config.grafana_port, config.grafana_host):
        resp = get("http://{}:{}/api/search/"
                   .format(config.grafana_host,
                           config.grafana_port),
                   auth=config.credentials)
    else:
        raise exceptions.ConnectionFailedException
    return resp.json()


def set_home_dashboard(dash_id):
    config = NS.conf
    if utils.port_open(config.grafana_port, config.grafana_host):
        resp = put('http://{}:{}/api/org/'
                   'preferences'.format(config.grafana_host,
                                        config.grafana_port),
                   headers=HEADERS,
                   auth=config.credentials,
                   data=json.dumps({"name": "Main Org.",
                                    "theme": "light",
                                    "homeDashboardId": dash_id}))
    else:
        raise exceptions.ConnectionFailedException
    return resp


def create_dashboard(dashboard_name, dashboard_dir=None):
    if not dashboard_dir:
        dashboard_dir = "/etc/tendrl/monitoring-integration/grafana/dashboards"
    dashboard_path = os.path.join(dashboard_dir,
                                  "{}.json".format(dashboard_name))

    if os.path.exists(dashboard_path):

        dashboard_data = utils.fread(dashboard_path)

        try:
            dashboard_json = json.loads(dashboard_data)
            response = _post_dashboard(dashboard_json)
            return response

        except exceptions.ConnectionFailedException:
            traceback.print_stack()
            raise exceptions.ConnectionFailedException

    else:
        raise exceptions.FileNotFoundException
