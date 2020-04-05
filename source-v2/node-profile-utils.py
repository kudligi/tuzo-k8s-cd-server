from ruamel.yaml import YAML
yaml = YAML()
yaml.indent(mapping=4, sequence=6, offset=4)

import json
import pprint as pp
import sys
import copy 
import os
from copy import deepcopy


def read_json(filename):
    with open(filename) as f:
        data = json.load(f)
        return data


def create_network_profile(topo, filepath):
    p1 = {
        "endorsingPeer" : True,
        "chaincodeQuery": True,
        "ledgerQeury"   : True,
        "eventSource"   : True,
    }

    org1 = {
        "mspid": "",
        "peers": [],
        "certificateAuthorities": [],
        "adminPrivateKey":  {"path":"artifacts/channel/crypto-config/peerOrganizations/DOMAIN/users/Admin@DOMAIN/msp/keystore/priv_sk"},
        "signedCert": {"path":"artifacts/channel/crypto-config/peerOrganizations/DOMAIN/users/Admin@DOMAIN/msp/signcerts/Admin@DOMAIN-cert.pem"}
    }

    p2 = {
        "url":"grpc://hlf-peer--ORGNAME--peerX:7051",
        "gprcOptions": {
            "ssl-target-name-override" : "peerX.DOMAIN"
        },
        "tlsCACerts": {
            "path" : "artifacts/channel/crypto-config/peerOrganizations/DOMAIN/peers/peerX.DOMAIN/tls/ca.crt"
        }
    }

    ord2 = {
        "url" : "grpc://hlf-orderer--NAME--ordererX:7050",
        "gprcOptions": {
            "ssl-target-name-override":"ordererX.DOMAIN"
        },
        "tlsCACerts":{
            "path": "artifacts/channel/crypto-config/ordererOrganizations/DOMAIN/orderers/ordererX.DOMAIN/tls/ca.crt"
        }
    }

    ca1 = {
        "url": "http://hlf-ca--orgname:7054",
        "httpOptions": {
            "verify" : "false"
        },
        "tlsCACerts" : {
            "path" : "artifacts/channel/crypto-config/peerOrganizations/DOMAIN/ca/ca.DOMAIN-cert.pem"
        },
        "registrar" : [{
            "enrollId": "admin",
            "enrollSecret" : "adminpw"
        }],
        "caName": "ca-ORGNAME"
    }

    ch1 = {"orderers":[], "peers": {}}

    profile ={
        "name" : "upaayan-loyalty-platform",
        "x-type" : "hlfv1",
        "description" : "Loyalty Points Network",
        "version" : "1.0",
        "channels" : {
            "common": {
                "orderers":[],
                "peers":{}
            }
        },
        "organizations" : {},
        "orderers"      : {},
        "peers"         : {},
        "certificateAuthorities": {}
    }

    # for channel in topo[""]

    for org in topo["orgs"]:
        for node in range(org["nodes"]):
            key = "peer" + str(node) + "." + org["domain"]
            profile["channels"]["common"]["peers"][key] = p1.copy()
            profile["peers"][key] = deepcopy(p2)
            profile["peers"][key]["url"] = profile["peers"][key]["url"].replace('X', str(node)).replace('ORGNAME', org['name'].lower())
            profile["peers"][key]["gprcOptions"]["ssl-target-name-override"] = profile["peers"][key]["gprcOptions"]["ssl-target-name-override"].replace('X', str(node)).replace('DOMAIN',  org['domain'])
            profile["peers"][key]["tlsCACerts"]["path"] = profile["peers"][key]["tlsCACerts"]["path"].replace('X', str(node)).replace('DOMAIN', org['domain']) 

    for orderer in topo["orderers"]:
        for node in range(orderer["nodes"]):
            key = "orderer" + str(node) + "." + orderer["domain"]
            profile["channels"]["common"]["orderers"].append(key)
            profile["orderers"][key] = deepcopy(ord2)
            profile["orderers"][key]["url"] = profile["orderers"][key]["url"].replace('X', str(node)).replace('NAME', orderer["name"].lower())
            profile["orderers"][key]["gprcOptions"]["ssl-target-name-override"] = profile["orderers"][key]["gprcOptions"]["ssl-target-name-override"].replace('X', str(node)).replace('DOMAIN', orderer["domain"])
            profile["orderers"][key]["tlsCACerts"]["path"] = profile["orderers"][key]["tlsCACerts"]["path"].replace('X', str(node)).replace('DOMAIN', orderer["domain"])
            


    for org in topo["orgs"]:
        profile["organizations"][org["name"]] = deepcopy(org1)
        profile["organizations"][org["name"]]["mspid"] = org["name"] + "MSP"
        profile["organizations"][org["name"]]["certificateAuthorities"].append("ca-" + org["name"])
        profile["organizations"][org["name"]]["adminPrivateKey"]["path"] = profile["organizations"][org["name"]]["adminPrivateKey"]["path"].replace('DOMAIN', org["domain"])
        profile["organizations"][org["name"]]["signedCert"]["path"] = profile["organizations"][org["name"]]["signedCert"]["path"].replace('DOMAIN', org["domain"])


        for node in range(org["nodes"]):
            profile["organizations"][org["name"]]["peers"].append("peer" + str(node) + "." + org["domain"])
    

    for org in topo["orgs"]:
        profile["certificateAuthorities"]["ca-"+org["name"]] = deepcopy(ca1)
        profile["certificateAuthorities"]["ca-"+org["name"]]["url"] = profile["certificateAuthorities"]["ca-"+org["name"]]["url"].replace("orgname", org["name"].lower())
        profile["certificateAuthorities"]["ca-"+org["name"]]["tlsCACerts"]["path"] =profile["certificateAuthorities"]["ca-"+org["name"]]["tlsCACerts"]["path"].replace("DOMAIN", org["domain"])
        profile["certificateAuthorities"]["ca-"+org["name"]]["caName"] = 'ca-' + org["name"]


    yaml.dump(profile, open(filepath, "w"))

def create_org_profile(topo, filepath):
    client_data = {
        "name" : "upaayan-loyalty-platform",
        "x-type" : "hlfv1",
        "description" : "Loyalty Points Network",
        "version" : "1.0",
        "client" : {   
            "organization" : "ORGNAME",
            "credentialStore" : {
                "path" : "fabric-client-kv-orgname",
                "cryptoStore" : {
                    "path" : "/tmp/fabric-client-kv-orgname"
                },
                "wallet" : "wallet-name"
            }
        }
    }

    for org in topo["orgs"]:
        d = deepcopy(client_data)
        d["client"]["organization"] = org["name"]
        d["client"]["credentialStore"]["path"] = d["client"]["credentialStore"]["path"].replace("orgname", org["name"].lower())
        d["client"]["credentialStore"]["cryptoStore"]["path"] = d["client"]["credentialStore"]["cryptoStore"]["path"].replace("orgname", org["name"].lower())
    
        filename = filepath + org["name"] + ".yaml"
        yaml.dump(d, open(filename, "w"))


data = read_json("./config_files/present_network/config.json")
create_network_profile(data, "./config_files/node-profiles/network-config.yaml")
create_org_profile(data, './config_files/node-profiles/')