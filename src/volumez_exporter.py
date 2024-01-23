import time
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server
import os
import json
import random
import requests

class VolumezExporter(object):
    def __init__(self):

        self.apitoken = os.environ['VOLUMEZ_TOKEN']
        url = "https://api.volumez.com"
        headers = {
            'Authorization': os.environ['VOLUMEZ_TOKEN'],
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers)
        

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
        healthcheck_response = requests.request("GET", url + '/healthcheck', headers=headers)
        healthcheck = healthcheck_response["Message"]

        # Metric Translations
        if healthcheck == 'ok':
            healthcheck = 0
        else:
            healthcheck = 1

        c = CounterMetricFamily("volumez_healthcheck", 'Overall Healthcheck...', labels=['volumez'])
        c.add_metric("prod", healthcheck)
        yield c


if __name__ == '__main__':
    start_http_server(8000)
    REGISTRY.register(VolumezExporter())
    while True:
        REGISTRY.collect()
        # lets not piss off the Site Reliability Teams at Volumez
        time.sleep(90)