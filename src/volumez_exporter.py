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

        # Metrics
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

        # media metrics
        media_response = requests.request("GET", url + '/media', headers=headers)
        media_list = media_response.json()
        blehmedias = []
        for media in media_list:
            print(media['node'])
            blehmedias.extend(media)

            for gar in blehmedias:
                if gar == 'state':
                    media_state = 0
                    c = CounterMetricFamily("volumez_media_" + gar, ' volumez media metrics...', labels=['instance'])

                    if media[gar] == 'online':
                        media_state = 1

                    c.add_metric([media['node']], media_state)
                    yield c
                c = CounterMetricFamily("volumez_media_" + gar, ' volumez media metrics...', labels=['instance'])
                #print(media[gar])
                if gar in media and type(media[gar]) != str:
                    c.add_metric([media['node']], media[gar])
                    yield c

        # nodes metrics
        nodes_response = requests.request("GET", url + '/nodes', headers=headers)
        nodes_list = nodes_response.json()
        blehnodes = []
        for nodes in nodes_list:
            print(nodes['instanceid'])
            blehnodes.extend(nodes)
            for gar in blehnodes:
                #print(gar + ":" + str(nodes[gar]))
                if gar == 'state':
                    node_state = 0
                    c = CounterMetricFamily("volumez_nodes_" + gar, ' volumez media metrics...', labels=['instance'])

                    if nodes[gar] == 'online':
                        node_state = 1

                    c.add_metric([nodes['instanceid']], node_state)
                    yield c
                
                c = CounterMetricFamily("volumez_nodes_" + gar, ' volumez nodes metrics...', labels=['instance'])
                if gar in nodes and type(nodes[gar]) != str:
                    c.add_metric([nodes['instanceid']], nodes[gar])
                    yield c

        # attachments metrics
        attachments_response = requests.request("GET", url + '/attachments', headers=headers)
        attachments_list = attachments_response.json()
        print(attachments_list)
        bleh = []
        for attachments in attachments_list:
            print(attachments['node'])
            bleh.extend(attachments)
            #print(bleh)
            for gar in bleh:
                print(gar + ":" + str(attachments[gar]))
                c = CounterMetricFamily("volumez_attachments_" + gar, ' volumez attachments metrics...', labels=['instance'])
                if type(attachments[gar]) != str:
                    c.add_metric([attachments['node']], attachments[gar])
                    yield c

        # tenant token
        auths_response = requests.request("GET", url + '/tenant/token', headers=headers)
        auths_list = auths_response.json()
        print(auths_list)

        # alerts, filed a bug
        #alerts_response = requests.request("GET", url + '/alerts', headers=headers)
        #alerts_list = alerts_response.json()
        #print(alerts_list)

if __name__ == '__main__':
    start_http_server(8000)
    REGISTRY.register(VolumezExporter())
    while True:
        REGISTRY.collect()
        print("Polling....")
        # lets not piss off the Site Reliability Teams at Volumez
        time.sleep(30)