import json
import pprint
from ruamel.yaml import YAML
yaml = YAML()
yaml.default_flow_style = None
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.width = 2048
import sys
pp = pprint.PrettyPrinter(indent=4)
import copy

def read_json(filename):
    with open(filename) as f:
        data = json.load(f)
        return data


net_configuration = read_json('../net.json')
pp.pprint(net_configuration)

channels = []
channel_dict = {}

for channel in net_configuration["Channels"]:
    channels.append({
        "name": channel["name"],
        "orgs": channel["orgs"]
    })
    channel_dict[channel["name"]] = channel["orgs"]

chaincodes = []

for chaincode in net_configuration["SmartContracts"]:
    l = channel_dict[chaincode["channel"]]
    s = [x + 'MSP.member' for x in l]
    s = ['\'' + x + '\'' for x in s]
    s = (', ').join(s)
    policy = 'OR(' + s + ')'
    print(policy)
    chaincodes.append({
        "name": chaincode["cc"],
        "version": '# "2.0"',
        "orgs": copy.deepcopy(channel_dict[chaincode["channel"]]),
        "channels": [{
            "name" : "common",
            "orgs" : copy.deepcopy(channel_dict[chaincode["channel"]]),
            "policy" : str(policy)
        }]
    })

network = {
    "network" : {
        "genesisProfile": "OrdererGenesis",
        "systemChannelID" : "testchainid",
        "channels": channels,
        "chaincodes": chaincodes
    }
}


FileName = "./temp.yaml"

yaml.dump(network, open(FileName, 'w'))

with open(FileName) as f:
    newText=f.read().replace('\\\"', '')
    newText=newText.replace('REMOVE_THIS_LINE', '')
    newText=newText.replace('\"\'', '\"')
    newText=newText.replace('\'#', '#')

with open(FileName, "w") as f:
    f.write(newText)
