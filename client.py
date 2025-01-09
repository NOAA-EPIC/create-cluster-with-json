#!/usr/bin/env python3                                                           
import requests                                                                  
import json                                                                      
import pprint as pp                                                              

class Client():                                                                  

    def __init__(self, url, header, displayname):                                             
        self.url = url                                                           
        self.api = url+'/api'                                                    
        self.header = header                                                     
        self.displayname = displayname
        self.session = requests.Session()                                        
        self.headers = {                                                         
            'Content-Type': 'application/json'                                   
        }                                                                        

    def get_resources(self):                                                     
        req = self.session.get(self.api + "/resources", headers=self.header)     
        req.raise_for_status()                                                   
        data = json.loads(req.text)                                              
        return data                                                              

    def get_resource(self, name):                                                
        req = self.session.get(self.api + "/resources", headers=self.header)     
        req.raise_for_status()                                                   
        data = json.loads(req.text)                                              

        resource = [x for x in data if x['name'].lower() == name.lower()]        

        return resource

    def create_v2_cluster(self, name: str, description: str, tags: str, type: str):
        if type != 'pclusterv2' and type != 'gclusterv2' and type != 'azclusterv2':
            raise Exception("Invalid cluster type")
        url = self.api + "/v2/resources"
        payload = {
            'name': name,
            'displayName': self.displayname,
            'description': description,
            'tags': tags,
            'type': type,
        }

        req = self.session.post(url, data=(payload), headers=self.header)
        req.raise_for_status()
        data = json.loads(req.text)
        return data

    def update_v2_cluster(self, id: str, cluster_definition):
        if id is None or id == "":
            raise Exception("Invalid cluster id")
        url = self.api + "/v2/resources/{}".format(id)
        req = self.session.put(url, json=cluster_definition, headers=self.header)
        req.raise_for_status()
        data = json.loads(req.text)
        return data

