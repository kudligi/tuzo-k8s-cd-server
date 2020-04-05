import sys

import copy   
import json
import pprint
pp = pprint.PrettyPrinter(indent=4)

from ruamel.yaml import YAML
yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)

################################## TEMPLATES for crypto-config ########################3
ordererOrgTemplate = {
    "Name": "insert here",
    "Domain": "insert here",
    "Specs": []
}

peerOrgTemplate = {
    "Name" : "insert here",
    "Domain": "insert here",
    "EnableNodeOUs": True,
    "Template": {
        "Count": "insert int no of nodes here"
    },
    "Users": {
        "Count": 1
    }
}



def read_json(filename):
    with open(filename) as f:
        data = json.load(f)
        return data

def create_cryptogen(topo, filepath):
    ## Populate Orderer Orgs
    OrdererOrgs = []
    if "orderers" not in topo:
        raise Exception('orderers field absent in network topology')
    orgs = topo["orderers"]
    for org in orgs:
        template = copy.deepcopy(ordererOrgTemplate)
        template["Name"] = org["name"]
        template["Domain"] = org["domain"]
        for i in range(org["nodes"]):
            template["Specs"].append({"Hostname":"orderer" + str(i)})
        OrdererOrgs.append(template.copy())

    pp.pprint(OrdererOrgs)


    ## Populate Orderer Orgs
    PeerOrgs = []
    if "orgs" not in topo:
        raise Exception('orgs field absent in network topology')

    orgs = topo["orgs"]
    for org in orgs:
        template = copy.deepcopy(peerOrgTemplate)
        template["Name"] = org["name"]
        template["Domain"] = org["domain"]
        template["Template"]["Count"] = org["nodes"]
        PeerOrgs.append(template.copy())
    
    pp.pprint(PeerOrgs)

    crypto_config = {
        "OrdererOrgs" : OrdererOrgs,
        "PeerOrgs"    : PeerOrgs
    }

    yaml.dump(crypto_config, open(filepath , "w"))


################################## TEMPLATES for configtx.yaml ########################3
ordererOrgConfigTemplate = {
    "Name": "XMSP",
    "ID": "XMSP",
    "MSPDir": "crypto-config/ordererOrganizations/DOMAIN/msp",
    "Policies": {
        "Readers" : {"Type": "Signature", "Rule":"OR('XMSP.member')"},
        "Writers" : {"Type": "Signature", "Rule":"OR('XMSP.member')"},
        "Admins" : {"Type": "Signature", "Rule":"OR('XMSP.member')"}
    }
}

peerOrgConfigTemplate = {
    "Name": "XMSP",
    "ID": "XMSP",
    "MSPDir": "crypto-config/peerOrganizations/DOMAIN/msp",
    "Policies": {
        "Readers" : {"Type": "Signature", "Rule":"OR('XMSP.admin', 'XMSP.peer', 'XMSP.client')"},
        "Writers" : {"Type": "Signature", "Rule":"OR('XMSP.admin', 'XMSP.client')"},
        "Admins" : {"Type": "Signature", "Rule":"OR('XMSP.admin')"}
    },
    "AnchorPeers": [{"Host" : "peer0.DOMAIN", "Port" : 7051}]
}


def create_configtx(topo, filepath):
    ## Populate Orgs
    Organizations = []
    
    if "orderers" not in topo:
        raise Exception('orderers field absent in network topology')

    orgs = topo["orderers"]
    for org in orgs:
        template = copy.deepcopy(ordererOrgConfigTemplate)
        template["Name"] = template["Name"].replace('X', org["name"])
        template["ID"] = template["ID"].replace('X', org["name"])
        template["MSPDir"] = template["MSPDir"].replace('DOMAIN', org['domain'])
        template["Policies"]["Readers"]["Rule"] = template["Policies"]["Readers"]["Rule"].replace('X', org["name"])
        template["Policies"]["Writers"]["Rule"] = template["Policies"]["Writers"]["Rule"].replace('X', org["name"])
        template["Policies"]["Admins"]["Rule"] = template["Policies"]["Admins"]["Rule"].replace('X', org["name"])
        Organizations.append(template.copy())

    
    orgs = topo["orgs"]
    for org in orgs:
        template = copy.deepcopy(peerOrgConfigTemplate)
        template["Name"] = template["Name"].replace('X', org["name"])
        template["ID"] = template["ID"].replace('X', org["name"])
        template["MSPDir"] = template["MSPDir"].replace('DOMAIN', org['domain'])
        template["Policies"]["Readers"]["Rule"] = template["Policies"]["Readers"]["Rule"].replace('X', org["name"])
        template["Policies"]["Writers"]["Rule"] = template["Policies"]["Writers"]["Rule"].replace('X', org["name"])
        template["Policies"]["Admins"]["Rule"] = template["Policies"]["Admins"]["Rule"].replace('X', org["name"])
        template["AnchorPeers"][0]["Host"] = template["AnchorPeers"][0]["Host"].replace("DOMAIN", org["domain"])
        Organizations.append(template.copy())

    ## Populate Capabilities
    Capabilities = {
        "Channel" : {
            "V1_4_3": True
        },
        "Orderer" : {
            "V1_4_2": True
        },
        "Application" : {
            "V1_4_2": True
        }
    }

    ## Populate Capabilities
    Application = {
        "Organizations" : [],
        "Policies"      : {
            "Readers": {"Type": "ImplicitMeta", "Rule": "ANY Readers"},
            "Writers": {"Type": "ImplicitMeta", "Rule": "ANY Writers"},
            "Admins": {"Type": "ImplicitMeta", "Rule": "MAJORITY Admins"}
        },
        "Capabilities" : Capabilities["Application"]
    }

    ## Populate Orderer section

    Orderer = {
        "OrdererType" : "etcdraft",
        "Addresses": [],
        "BatchTimeout" : "1s",
        "BatchSize": {
            "MaxMessageCount": 5,
            "AbsoluteMaxBytes": "98 MB",
            "PreferredMaxBytes": "1024 KB"
        },
        "EtcdRaft" : {
            "Consenters": [],
            "Options" : {
                "TickInterval": "500ms",
                "ElectionTick": 10,
                "HeartbeatTick": 1,
                "MaxInflightBlocks": 5,
                "SnapshotIntervalSize": "20 MB"
            }
        },
        "Organizations": [],
        "Policies": {
            "Readers": {"Type": "ImplicitMeta", "Rule": "ANY Readers"},
            "Writers": {"Type": "ImplicitMeta", "Rule": "ANY Writers"},
            "Admins": {"Type": "ImplicitMeta", "Rule": "MAJORITY Admins"},
            "BlockValidation": { "Type": "ImplicitMeta" , "Rule": "ANY Writers"}
        },
        "Capabilities" :  Capabilities["Orderer"]

    }

    consenterTemplate = {
        "Host": "ORDERER.DOMAIN",
        "Port": 7059,
        "ClientTLSCert": "crypto-config/ordererOrganizations/DOMAIN/orderers/ORDERER.DOMAIN/tls/server.crt",
        "ServerTLSCert": "crypto-config/ordererOrganizations/DOMAIN/orderers/ORDERER.DOMAIN/tls/server.crt"
    }

    for org in topo["orderers"]:
        for i in range(org["nodes"]):
            d = consenterTemplate.copy()
            d["Host"] = d["Host"].replace("ORDERER", 'orderer' + str(i)).replace("DOMAIN", org["domain"])
            d["ClientTLSCert"] = d["ClientTLSCert"].replace("ORDERER", 'orderer' + str(i)).replace("DOMAIN", org["domain"])
            d["ServerTLSCert"] = d["ServerTLSCert"].replace("ORDERER", 'orderer' + str(i)).replace("DOMAIN", org["domain"])
            Orderer["EtcdRaft"]["Consenters"].append(d.copy())

    Orderer["Addresses"].append(Orderer["EtcdRaft"]["Consenters"][0]["Host"] + ":7050")
    ## Populate Channel section
    Channel = {
        "Policies" : {
            "Readers": {"Type": "ImplicitMeta", "Rule": "ANY Readers"},
            "Writers": {"Type": "ImplicitMeta", "Rule": "ANY Writers"},
            "Admins": {"Type": "ImplicitMeta", "Rule": "MAJORITY Admins"}
        }, 
        "Capabilities" : Capabilities["Channel"]
    }


    ## Populate Profiles section
    channelTemplate = {
        "Consortium" : "TheConsortium",
        "Application": {
            "Organizations" : []
        }
    }

    channelTemplate.update(Channel)
    channelTemplate["Application"].update(Application)


    Profiles = {
        "OrdererGenesis" : {
            "Orderer" : {
                "Organizations" : []
            },
            "Consortiums": {
                "TheConsortium": {
                    "Organizations" : []
                }
            }
        },
    }

    Profiles["OrdererGenesis"].update(Channel)
    Profiles["OrdererGenesis"]["Orderer"].update(Orderer)
    Profiles["OrdererGenesis"]["Orderer"]["Organizations"] = []
    
    for org in Organizations:
        if "AnchorPeers" not in org:
            Profiles["OrdererGenesis"]["Orderer"]["Organizations"].append(org)
        else:
            Profiles["OrdererGenesis"]["Consortiums"]["TheConsortium"]["Organizations"].append(org)
    
    channels = topo["channels"]

    for channel in channels:
        template = copy.deepcopy(channelTemplate)
        for org in Organizations:
            if org["Name"][:-3] in channel["orgs"]:
                template["Application"]["Organizations"].append(org)
        Profiles[channel["name"]] = template.copy() 
    
    configtx = {
        "Organizations" : Organizations,
        "Capabilities"  : Capabilities, 
        "Application"   : Application,
        "Orderer"   : Orderer,
        "Channel"   : Channel,
        "Profiles"  : Profiles
    }

    


    yaml.dump(configtx, open(filepath, "w"))

    with open(filepath, 'r') as f:
       newText=f.read().replace('[]', '')
       open(filepath, 'w').write(newText)



def create_network(topo, filepath):
    Network = {
        "tlsEnabled" : False,
        "useActualDomains": True,
        "network" : {
            "genesisProfile": "OrdererGenesis",
            "systemChannelID": "testchainid",
            "channels": [],
            "chaincodes": []
        }
    }

    channels = topo["channels"]
    ch_dict = {}
    for channel in channels:
        d = {"name" : channel["name"], "orgs" : channel["orgs"]}
        ch_dict[channel["name"]] = channel["orgs"]
        Network["network"]["channels"].append(channel)

    chaincodes = topo["contracts"]
    for cc in chaincodes:
        d = {
            "name": cc["contract"],
            "Version": "REMOVE THIS LINE",
            "orgs": [],
            "channels":[]
        }
        for ch in cc["channels"]:
            d["orgs"] = list(set(d["orgs"]) | set(ch_dict[ch]))
            b = {
                "name": ch,
                "orgs": ch_dict[ch],
                "policy": ''
            }
            s = [x + 'MSP.member' for x in ch_dict[ch]]
            s = ['\'' + x + '\'' for x in s]
            s = (', ').join(s)
            b["policy"] = 'OR(' + s + ')'
            d["channels"].append(b.copy())
        
        Network["network"]["chaincodes"].append(d.copy())

    yaml = YAML()
    yaml.default_flow_style = None
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 2048
    yaml.dump(Network, open(filepath, "w"))
    with open(filepath, 'r') as f:
        newText=f.read().replace('REMOVE THIS LINE', '#v2')
        open(filepath, 'w').write(newText)


## Read Data from the network topology json file
# data = read_json('./network_topology.json')

# #generate crypto-config.yaml
# create_cryptogen(data)

# #generate configtx.yaml
# create_configtx(data)

# #generate network.yaml
# create_network(data)