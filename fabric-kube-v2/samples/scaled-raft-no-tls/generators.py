import sys

import copy   
import json
import pprint
pp = pprint.PrettyPrinter(indent=4)

from ruamel.yaml import YAML
yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)

################################## TEMPLATES ########################3
ordererOrgTemplate = {
    "Name": "insert here",
    "Domain": "insert here",
    "Specs": []
}



def read_json(filename):
    with open(filename) as f:
        data = json.load(f)
        return data

def create_cryptogen(topo):
    ## Populate Orderer Orgs
    OrdererOrgs = []
    if "orderers" not in topo:
        raise Exception('orderers field absent in network topology')
    orgs = topo["orderers"]
    for org in orgs:
        template = copy.deepcopy(ordererOrgTemplate)
        template["Name"] = org["name"]
        template["Domain"] = org["domain"]
        for i in org["nodes"]
            template["specs"].append({"Hostname":"orderer" + str(i)})
        OrdereOrgs.append(template.copy())

    pp.pprint(OrdererOrgs)

    # PeerOrgs = []


data = read_json('./network_topology.json')
create_cryptogen(data)