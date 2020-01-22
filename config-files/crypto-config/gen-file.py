import json
import pprint
from ruamel.yaml import YAML
yaml = YAML()
import sys
pp = pprint.PrettyPrinter(indent=4)
yaml.indent(mapping=2, sequence=4, offset=2)
import copy


def read_json(filename):
    with open(filename) as f:
        data = json.load(f)
        return data

OrderOrgs = {
    "Name":"OrdererAuthority",
    "Domain":"ordererauthority.organizations",
    "Specs":[{
        "Hostname": "orderer0"
    }]
    }

PeerOrgTemplate = {
    "Name": "",
    "Domain": "",
    "EnableNodeOUs": True,
    "Template": {
        "Count" : 1
    },
    "Users":{
        "Count" : 1
    }
}


net_configuration = read_json('../net.json')
pp.pprint(net_configuration)

crypto_config_dict = {
    "OrdererOrgs":[OrderOrgs],
    "PeerOrgs":[]
} 


peer = copy.deepcopy(PeerOrgTemplate)
peer["Name"] = net_configuration["LeadOrganization"]["name"]
peer["Domain"] = net_configuration["LeadOrganization"]["domain"]
crypto_config_dict["PeerOrgs"].append(peer)


for peerOrg in net_configuration["OtherOrganizations"]:
    peer = copy.deepcopy(PeerOrgTemplate)
    peer["Name"] = peerOrg["name"]
    peer["Domain"] = peerOrg["domain"]
    crypto_config_dict["PeerOrgs"].append(peer)


yaml.dump(crypto_config_dict, open("./temp.yaml", 'w'))
