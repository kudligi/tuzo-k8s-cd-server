from ruamel.yaml import YAML
yaml = YAML()
import json
import pprint as pp
import sys
import copy 
import os

yaml.indent(mapping=4, sequence=6, offset=4)

client_data = {
    "name" : "upaayan-loyalty-LeadMerchant",
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

def read_json(filename):
    with open(filename) as f:
        data = json.load(f)
        return data

net_file = "../config-files/generated_network_config/" + sys.argv[1]

net = read_json(net_file)

# pp.pprint(net)
net["OtherOrganizations"].append(net["LeadOrganization"])

i = 1
for org in net["OtherOrganizations"] :
    d = copy.deepcopy(client_data)
    d["client"]["organization"] = org["name"]
    d["client"]["credentialStore"]["path"] = d["client"]["credentialStore"]["path"].replace("orgname", org["name"].lower())
    d["client"]["credentialStore"]["cryptoStore"]["path"] = d["client"]["credentialStore"]["cryptoStore"]["path"].replace("orgname", org["name"].lower())
    
    FileName = "./org" + str(i) + ".yaml"
    yaml.dump(d, open(FileName, 'w'))
    
    i = i + 1