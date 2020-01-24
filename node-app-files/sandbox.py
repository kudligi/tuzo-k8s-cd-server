from ruamel.yaml import YAML
yaml = YAML()
import json
import pprint as pp
import sys
import copy 

yaml.indent(mapping=4, sequence=6, offset=4)

def read_json(filename):
    with open(filename) as f:
        data = json.load(f)
        return data


filename = "network-config.yaml"

net_file = "../config-files/generated_network_config/" + sys.argv[1]

net = read_json(net_file)

data = yaml.load(open(filename))

#pp.pprint(data)



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
    "adminPrivateKey":  {"path":""},
    "signedCert": {"path":""}
}

p2 = {
    "url":"grpc://hlf-peer--ORGNAME--peer0:7051",
    "gprcOptions": {
        "ssl-target-name-override" : "peer0.DOMAIN"
    },
    "tlsCACerts": {
        "path" : "artifacts/channel/crypto-config/peerOrganizations/DOMAIN/orderers/peer0.DOMAIN/tls/ca.crt"
    }
}

ca1 = {
    "url": "",
    "httpOptions": {
        "verify" : "false"
    },
    "tlsCACerts" : {
        "path" : ""
    },
    "registrar" : [{
        "enrollId": "admin",
        "enrollSecret" : "adminpw"
    }],
    "caName": "ca-ORGNAME"
}

d = {
    "name" : "upaayan-loyalty-" + net["LeadOrganization"]["name"],
    "x-type" : "hlfv1",
    "description" : "Loyalty Points Network",
    "version" : "1.0",
    "channels" : {
        "common": {
            "orderers":["orderer0.ordererauthority.organizations"]
        },
        "peers": {}
    },
    "organizations": {},
    "orderers": {
        "orderer0.orderer.organizations":{
            "url": "grpc://hlf-orderer--ordererauthority--orderer0:7050",
            "gprcOptions": {
                "ssl-target-name-override" : "orderer0.ordererauthority.organizations"
            },
            "tlsCACerts": {
                "path" : "artifacts/channel/crypto-config/ordererOrganizations/ordererauthority.organizations/orderers/orderer0.ordererauthority.organizations/tls/ca.crt"
            }
        }
    },
    "peers": {},
    "certificateAuthorities": {}

}

org = net["LeadOrganization"]
d["organizations"][org["name"]] = copy.deepcopy(org1) 
d["organizations"][org["name"]]["mspid"] = org["name"] + "MSP"
d["organizations"][org["name"]]["peers"].append("peer0."+org["domain"] )
d["organizations"][org["name"]]["certificateAuthorities"].append("ca-"+org["name"])
d["organizations"][org["name"]]["adminPrivateKey"]["path"] = "artifacts/channel/crypto-config/peerOrganizations/DOMAIN/users/Admin@DOMAIN/msp/keystore/KEY".replace("DOMAIN", org["domain"])
d["organizations"][org["name"]]["signedCert"]["path"] = "artifacts/channel/crypto-config/peerOrganizations/DOMAIN/users/Admin@DOMAIN/msp/signcerts/Admin@DOMAIN-cert.pem".replace("DOMAIN", org["domain"])


for org in net["OtherOrganizations"]:
    d["organizations"][org["name"]] = copy.deepcopy(org1) 
    d["organizations"][org["name"]]["mspid"] = org["name"] + "MSP"
    d["organizations"][org["name"]]["peers"].append("peer0."+org["domain"] )
    d["organizations"][org["name"]]["certificateAuthorities"].append("ca-"+org["name"])
    d["organizations"][org["name"]]["adminPrivateKey"]["path"] = "artifacts/channel/crypto-config/peerOrganizations/DOMAIN/users/Admin@DOMAIN/msp/keystore/KEY".replace("DOMAIN", org["domain"])
    d["organizations"][org["name"]]["signedCert"]["path"] = "artifacts/channel/crypto-config/peerOrganizations/DOMAIN/users/Admin@DOMAIN/msp/signcerts/Admin@DOMAIN-cert.pem".replace("DOMAIN", org["domain"])

org = net["LeadOrganization"]
d["channels"]["peers"]["peer0." + org["domain"]] = copy.deepcopy(p1)
for org in net["OtherOrganizations"]:
    d["channels"]["peers"]["peer0." + org["domain"]] = copy.deepcopy(p1)
    
org = net["LeadOrganization"]
d["peers"]["peer0." + org["domain"]] = copy.deepcopy(p2)
d["peers"]["peer0." + org["domain"]]["url"] = d["peers"]["peer0." + org["domain"]]["url"].replace('ORGNAME', org["name"]) 
for org in net["OtherOrganizations"]:
    d["peers"]["peer0." + org["domain"]] = copy.deepcopy(p2)
    d["peers"]["peer0." + org["domain"]]["url"] = d["peers"]["peer0." + org["domain"]]["url"].replace('ORGNAME', org["name"].lower()) 
    d["peers"]["peer0." + org["domain"]]["gprcOptions"]["ssl-target-name-override"] = d["peers"]["peer0." + org["domain"]]["gprcOptions"]["ssl-target-name-override"].replace('DOMAIN', org["domain"])
    d["peers"]["peer0." + org["domain"]]["tlsCACerts"]["path"] = d["peers"]["peer0." + org["domain"]]["tlsCACerts"]["path"].replace('DOMAIN', org["domain"])

yaml.dump(d, open("./temp.yaml", 'w'))