import time
import os
import requests
import json
import sys

from warrant import Cognito
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server

'''
New logic:

Loop over attachments, for each attachment that is attached:
    node status for the found node
        media status for all media associated with the node
    volume status for each found attached volume

'''

class VolumezExporter(object):
    def __init__(self):

        self.access_token = self.get_access_token()
        self.clusterid = os.environ['VLZ_CLUSTERID']

        #self.refresh_token = self.trade_for_refresh_token()
        #print(self.refresh_token)

        

    def collect(self):

        try:
            # Requests fodder
            url = "https://api.volumez.com"

            headers = {
                'Authorization': self.access_token, # needs to be refresh_token
                'Content-Type': 'application/json'
            }
            # print(headers)
            healthcheck = 0
            healthcheck_response = requests.request("GET", url + '/healthcheck', headers=headers)
            healthcheckdict = healthcheck_response.json()
            healthcheck = healthcheckdict["Message"]

            # Metric Translations
            if healthcheck == 'ok':
                healthcheck = 1
            else:
                healthcheck = 0
            
            # print(str(healthcheck))
            c = CounterMetricFamily("volumez_healthcheck", 'Overall Healthcheck Example...', labels=['clusterid'])
            c.add_metric([self.clusterid], healthcheck)
            yield c

            # top level, attachments metrics
            # This helps only care about attached nodes, volumes and media
            attachments_response = requests.request("GET", url + '/attachments', headers=headers)
            media_response = requests.request("GET", url + '/media', headers=headers)
            volumes_response = requests.request("GET", url + '/volumes', headers=headers)
            jobs_response = requests.request("GET", url + '/jobs', headers=headers)


            attachments_list = attachments_response.json()
            media_list = media_response.json()
            volumes_list = volumes_response.json()
            jobs_list = jobs_response.json()

            # attachment status counts, high level indicator
            c = CounterMetricFamily("volumez_" + "attachments" + "_count", ' volumez count metrics...', labels=['clusterid'])
            c.add_metric([self.clusterid], len(attachments_list))
            yield c
            # online
            list_container = []
            for thing in attachments_list:
                if thing["state"] == "online":
                    list_container.append(thing)
            count = len(list_container)
            print(count)
            c = CounterMetricFamily("volumez_" + "attachments" + "_online_count", ' volumez online count metrics...', labels=['clusterid'])
            c.add_metric([self.clusterid], count)
            yield c
            # degraded
            list_container = []
            for thing in attachments_list:
                if thing["state"] == "degraded":
                    list_container.append(thing)
            count = len(list_container)
            print(count)
            c = CounterMetricFamily("volumez_" + "attachments" + "_degraded_count", ' volumez degraded count metrics...', labels=['clusterid'])
            c.add_metric([self.clusterid], count)
            yield c     


            # non-zero statuses
            # attachments
            list_container = []
            for thing in attachments_list:
                if thing["status"] != "":
                    list_container.append(thing)
            count = len(list_container)
            print(count)
            c = CounterMetricFamily("volumez_" + "attachments" + "_nonzero_status", ' volumez nonzero metrics...', labels=['clusterid'])
            c.add_metric([self.clusterid], count)
            yield c
            # media
            list_container = []
            for thing in media_list:
                if thing["status"] != "":
                    print(thing["status"])
                    list_container.append(thing)
            count = len(list_container)
            print(count)
            c = CounterMetricFamily("volumez_" + "media" + "_nonzero_status", ' volumez nonzero metrics...', labels=['clusterid'])
            c.add_metric([self.clusterid], count)
            yield c
            # volumes
            list_container = []
            for thing in volumes_list:
                if thing["status"] != "":
                    print(thing["status"])
                    list_container.append(thing)
            count = len(list_container)
            print(count)
            c = CounterMetricFamily("volumez_" + "volumes" + "_nonzero_status", ' volumez nonzero metrics...', labels=['clusterid'])
            c.add_metric([self.clusterid], count)
            yield c
            # jobs
            list_container = []
            for thing in jobs_list:
                if thing["status"] != "":
                    print(thing["status"])
                    list_container.append(thing)
            count = len(list_container)
            print(count)
            c = CounterMetricFamily("volumez_" + "jobs" + "_nonzero_status", ' volumez nonzero metrics...', labels=['clusterid'])
            c.add_metric([self.clusterid], count)
            yield c

            # attachments
            print("attachments call..." + str(len(attachments_list)))
            attachments_container = []
            for attachments in attachments_list:
                #print(attachments['node'])
                attachments_container.extend(attachments)

                for attachment in attachments_container:
                    # Grab the state of the attachments
                    #print(attachment + ":" + str(attachments[attachment]))
                    if attachment == 'state':
                        attachment_state = 0
                        if attachments[attachment] == 'online':
                            attachment_state = 1
                        #c = CounterMetricFamily("volumez_attachments_" + attachment, ' volumez attachments metrics...', labels=['instance','volumeid','mountpoint'])
                        #c.add_metric([attachments['node'], attachments['volumeid'], attachments['mountpoint']], attachment_state)
                        #yield c
                # Grab the state of the nodes in the attachments
                nodes_response = requests.request("GET", url + '/nodes/' + attachments["node"], headers=headers)
                print("node call...")
                nodes_obj = nodes_response.json()
                #if nodes_obj['state']: # == attachments['node']:
                node_state = 0
                c = CounterMetricFamily("volumez_nodes_state", ' volumez media metrics...', labels=['instance','clusterid'])
                if nodes_obj['state'] == "online":
                    node_state = 1
                c.add_metric([nodes_obj['instanceid'],self.clusterid], node_state)
                yield c
                # Grab the metrics from the attached media of the attached nodes
                media_list = media_response.json()
                print("media call..." + str(len(media_list)))
                media_container = []
                for medias in media_list:
                    if medias["node"] == attachments["node"] and not medias['mediaid'].startswith("ram"):
                        media_container.extend(medias)
                        for media in media_container:
                            media = media.lower()
                            if media == 'state':
                                media_state = 0
                                c = CounterMetricFamily("volumez_media_" + media, ' volumez media metrics...', labels=['instance','mediaid','clusterid'])

                                if medias[media] == 'online':
                                    media_state = 1
                                c.add_metric([medias['node'],medias['mediaid'],self.clusterid], media_state)
                                yield c
                            if media in medias and type(medias[media]) != str:
                                #print("in media...")
                                if not medias['mediaid'].startswith("ram"):
                                    #print(medias['mediaid'])
                                    c = CounterMetricFamily("volumez_media_" + media, ' volumez media metrics...', labels=['instance','mediaid','clusterid'])
                                    c.add_metric([medias['node'],medias['mediaid'],self.clusterid], medias[media])
                                    yield c
                # Grab the status of the volume associated with the node, attachment, and media
                volumes_list = volumes_response.json()
                # print(volumes_list)
                volumes_container = []
                for volumes in volumes_list:
                    if volumes["volumeid"] == attachments['volumeid']:
                        volumes_container.extend(volumes)
                        for volume in volumes_container:
                            #print(volume + ":" + str(volumes[volume]))
                            #if volume['owner'] != "":
                            volume = volume.lower()
                            if volume == 'state':
                                volume_state = 0
                                c = CounterMetricFamily("volumez_volumes_" + volume, ' volumez volumes metrics...', labels=['volumeid','name','clusterid'])

                                if volumes[volume] == 'online':
                                    volume_state = 1

                                c.add_metric([volumes['volumeid'],volumes['name'],self.clusterid], volume_state)
                                yield c
                            if volume in volumes and type(volumes[volume]) != str and volumes[volume]:
                                c = CounterMetricFamily("volumez_volumes_" + volume, ' volumez volumes metrics...', labels=['volumeid','name','clusterid'])
                                c.add_metric([volumes['volumeid'],volumes['name'],self.clusterid], volumes[volume])
                                yield c
        except Exception as e:
            print(e)
            sys.exit(str(e))
        print("done...")                             

    def get_access_token(self):
        
        try:
            user_pool_id = os.environ['VLZ_USERPOOLID'] # vlz iss us-east-1_j38QatKuM
            username = os.environ['VLZ_USER']
            password = os.environ['VLZ_PASS']
            clientid = os.environ['VLZ_CLIENTID'] # vlz aud 34056a7lv9hg5opb7heqjvafv0

            try:
                u = Cognito(
                    user_pool_id=user_pool_id,
                    client_id=clientid,
                    user_pool_region="us-east-1", # needed by warrant, should be derived from poolid doh
                    username=username
                )
                u.authenticate(password=password)
            except Exception as p:
                print(p)
                sys.exit(str(p))
        except Exception as e:
            print(e)
            sys.exit(str(e))

        return u.id_token
    
    def trade_for_refresh_token(self):

        # Requests fodder
        url = "https://api.volumez.com"

        headers = {
            #'accesstoken': self.access_token,
            'Content-Type': 'application/json'
        }
        payload = {
            'accesstoken': self.access_token,
            'hostname': 'fhirwatch-pop-os'
        }
        print(self.access_token)
        try:
            # tenant token
            # httpss://api.volumez.com/dev/tenant/apiaccess/credentials/refresh
            auths_response = requests.request("POST", url + '/tenant/refreshtoken', headers=headers, data=json.dumps(payload))
            auths_list = auths_response.json()
            print(auths_list)
        
        except Exception as e:
            print(e)

        return auths_list

    def refresh_token(self):

        # Requests fodder
        url = "https://api.volumez.com"

        headers = {
            'Authorization': self.access_token,
            'Content-Type': 'application/json'
        }

        try:
            pass
        
        except Exception as e:
            print(e)
        
        return "gar" #auths_list["thinger"]


if __name__ == '__main__':

    polling_cycle = os.environ['VLZ_POLLING'] # make configurable for 429 hell
    start_http_server(8000)
    REGISTRY.register(VolumezExporter())
    while True:
        try:
            REGISTRY.collect()
            print("Polling Volumez API for metrics data....")
            #looped e loop
            time.sleep(int(polling_cycle))
        except Exception as e:
            print(e)
            sys.exit(str(e))
        #else:
        #    break

        # scratch
        # alerts, filed a bug
        #alerts_response = requests.request("GET", url + '/alerts', headers=headers)
        #alerts_list = alerts_response.json()
        #print(alerts_list)
        # here id like to expose "count" to Coralogix to watch for change on the integer

        # jobs metrics
        #jobs_response = requests.request("GET", url + '/jobs', headers=headers)
        #jobs_list = jobs_response.json()
        #print(jobs_list)
        #jobs_container = []
        #for jobs in jobs_list:
            #print(jobs['object'])
        #    jobs_container.extend(jobs)

        #    for job in jobs_container:
                #print(job + ":" + str(jobs[job]))
        #        c = CounterMetricFamily("volumez_jobs_" + job, ' volumez jobs metrics...', labels=['instance'])
        #        if type(jobs[job]) != str:
        #            c.add_metric([jobs['object']], jobs[job])
        #            yield c
        