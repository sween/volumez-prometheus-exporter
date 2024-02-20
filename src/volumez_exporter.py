import time
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server
import os
import requests

class VolumezExporter(object):
    def __init__(self):

        self.apitoken = os.environ['VOLUMEZ_TOKEN']
        self.tenantid = os.environ['VOLUMEZ_TENANT']

    def collect(self):

        # Requests fodder
        url = "https://api.volumez.com"

        headers = {
            'Authorization': self.apitoken,
            'Content-Type': 'application/json'
        }

        # Get the Data
        # simple healthcheck
        '''
        {
            "Message": "ok"
        }
        '''
        healthcheck = 0
        healthcheck_response = requests.request("GET", url + '/healthcheck', headers=headers)
        healthcheckdict = healthcheck_response.json()
        healthcheck = healthcheckdict["Message"]

        # Metric Translations
        if healthcheck == 'ok':
            healthcheck = 1
        else:
            healthcheck = 0
        print(str(healthcheck))
        c = CounterMetricFamily("volumez_healthcheck", 'Overall Healthcheck Example...', labels=['tenant'])
        c.add_metric([self.tenantid], healthcheck)
        yield c


if __name__ == '__main__':
    start_http_server(8000)
    REGISTRY.register(VolumezExporter())
    while True:
        REGISTRY.collect()
        print("Polling....")
        # lets not piss off the Site Reliability Teams at Volumez
        time.sleep(90)