import json
import pprint
from ruamel.yaml import YAML
yaml = YAML()
import sys
pp = pprint.PrettyPrinter(indent=4)
import copy

def read_json(filename):
    with open(filename) as f:
        data = json.load(f)
        return data


net_configuration = read_json('../net.json')
#pp.pprint(net_configuration)

Organizations = []

Orderer = {
    "Name": "OrdererAuthorityMSP",
    "ID": "OrdererAuthorityMSP",
    "MSPDir": "crypto-config/ordererOrganizations/ordererauthority.organizations/msp",
    "Policies": {
        "Readers" :{
            "Type": "Signature",
            "Rule": '"OR(\'OrdererAuthorityMSP.member\')"'
        },
        "Writers": {
            "Type": "Signature",
            "Rule": '"OR(\'OrdererAuthorityMSP.member\')"'
        },
        "Admins": {
            "Type": "Signature",
            "Rule": '"OR(\'OrdererAuthorityMSP.admin\')"'
        
        }
    }

}

Organizations.append(Orderer)

PeerOrgTemplate = {
    "Name": "",
    "ID": "",
    "Policies":{
        "Readers" :{
            "Type": "Signature",
            "Rule": '\"OR(\'MSP.admin\', \'MSP.peer\', \'MSP.client\')\"'
        },
        "Writers": {
            "Type": "Signature",
            "Rule": '\"OR(\'MSP.admin\', \'MSP.client\')\"'
        },
        "Admins": {
            "Type": "Signature",
            "Rule": '\"OR(\'MSP.admin\')\"'
        
        }
    },
    "AnchorPeers" : [
        {
            "Host": "hlf-peer--ORGNAME--peer0",
            "Port": 7051
        }
    ]
}

peerOrg = net_configuration["LeadOrganization"]
d = dict()
d["Name"] =  peerOrg["name"] + 'MSP'
d["ID"] = peerOrg["name"] + 'MSP'
d["MSPDir"] = "crypto-config/peerOrganizations/" + peerOrg["domain"] + "/msp"
d["Policies"] = copy.deepcopy(PeerOrgTemplate['Policies'])
d["Policies"]["Readers"]["Rule"] = '\"OR(\'MSP.admin\', \'MSP.peer\', \'MSP.client\')\"'.replace('MSP', peerOrg["name"]+'MSP')
d["Policies"]["Writers"]["Rule"] = '\"OR(\'MSP.admin\', \'MSP.client\')\"'.replace('MSP', peerOrg["name"]+'MSP')
d["Policies"]["Admins"]["Rule"] = '\"OR(\'MSP.admin\')\"'.replace('MSP', peerOrg["name"]+'MSP')
Organizations.append(d.copy())


for peerOrg in net_configuration["OtherOrganizations"]:
    d = dict()
    d["Name"] =  peerOrg["name"] + 'MSP'
    d["ID"] = peerOrg["name"] + 'MSP'
    d["MSPDir"] = "crypto-config/peerOrganizations/" + peerOrg["domain"] + "/msp"
    d["Policies"] = copy.deepcopy(PeerOrgTemplate['Policies'])
    d["Policies"]["Readers"]["Rule"] = '"OR(\'MSP.admin\', \'MSP.peer\', \'MSP.client\')"'.replace('MSP', peerOrg["name"]+'MSP')
    d["Policies"]["Writers"]["Rule"] = '"OR(\'MSP.admin\', \'MSP.client\')"'.replace('MSP', peerOrg["name"]+'MSP')
    d["Policies"]["Admins"]["Rule"] = '\"OR(\'MSP.admin\')\"'.replace('MSP', peerOrg["name"]+'MSP')
    
    # peer.append(dict(PeerOrgTemplate))
    # peer[i]["Name"]: peerOrg["name"]
    # peer[i]["ID"]: peerOrg["name"]
    # peer[i]["Policies"]["Readers"]["Rule"] = PeerOrgTemplate["Policies"]["Readers"]["Rule"].replace('MSP', peerOrg["name"]+'MSP')
    # peer[i]["Policies"]["Writers"]["Rule"] = PeerOrgTemplate["Policies"]["Writers"]["Rule"].replace('MSP', peerOrg["name"]+'MSP')
    # peer[i]["Policies"]["Admins"]["Rule"] = PeerOrgTemplate["Policies"]["Admins"]["Rule"].replace('MSP', peerOrg["name"]+'MSP')
    # peer[i]["AnchorPeers"][0]["Host"] = PeerOrgTemplate["AnchorPeers"][0]["Host"].replace('ORGNAME', peerOrg["name"].lower())
    # pp.pprint(peer[i])
    Organizations.append(d.copy())


Capabilities = {
    "Channel" : {'V1_4_2':True},
    "Orderer" : {'V1_4_2':True},
    "Application" : {'V1_4_2':True}
}

Application = {
    "Organizations": "REMOVE_THIS_LINE",
    "Policies": {
        "Readers":{
            "Type": "ImplicitMeta",
            "Rule": "\"ANY Readers\""
        },
        "Writers":{
            "Type": "ImplicitMeta",
            "Rule": "\"ANY Writers\""
        },
        "Admins":{
            "Type": "ImplicitMeta",
            "Rule": "\"MAJORITY Admins\""
        }
    },
    "Capabilities": Capabilities["Application"]
}

Orderer = {
    "OrdererType": "solo",
    "Addresses": ["hlf-orderer--ordererauthority--orderer0:7050"],
    "BatchTimeout": "1s",
    "BatchSize":{
        "MaxMessageCount": 5,
        "AbsoluteMaxBytes": "98 MB",
        "PreferredMaxBytes": "1024 KB"
    },
    "Organizations": "REMOVE_THIS_LINE",
    "Policies": {
        "Readers":{
            "Type": "ImplicitMeta",
            "Rule": '\"ANY Readers\"'
        },
        "Writers":{
            "Type": "ImplicitMeta",
            "Rule": '\"ANY Writers\"'
        },
        "Admins":{
            "Type": "ImplicitMeta",
            "Rule": '\"MAJORITY Admins\"'
        }, 
        "BlockValidation": {
            "Type": "ImplicitMeta",
            "Rule": '\"ANY Writers\"'
        }   
    }, 
    "Capabilities": Capabilities["Orderer"]
}

Channel = {
    "Policies": {
        "Readers":{
            "Type": "ImplicitMeta",
            "Rule": '\"ANY Readers\"'
        },
        "Writers":{
            "Type": "ImplicitMeta",
            "Rule": '\"ANY Writers\"'
        },
        "Admins":{
            "Type": "ImplicitMeta",
            "Rule": '\"MAJORITY Admins\"'
        }
    },
    "Capabilities": Capabilities["Channel"]
}

Peers = copy.deepcopy(Organizations[1:])

Profiles = {
    "OrdererGenesis": {
        "Orderer"   : {} ,
        "Consortiums": {
            "TheConsortium" : {
                "Organizations": Organizations[1:]
            }
        }
    }
}

Profiles["OrdererGenesis"]["Orderer"].update(Orderer)
Profiles["OrdererGenesis"]["Orderer"]["Organizations"] = [Organizations[0]]


common = {
    "Consortium": "TheConsortium",
    "Application": {}
}

for k in Application:
    common["Application"][k] = Application[k]

common["Application"]["Organizations"] = Organizations[1:]

common.update(Channel)



Profiles["OrdererGenesis"].update(Channel)

Profiles["common"] = common


configtx_dict = {
    "Organizations": Organizations,
    "Capabilities" : Capabilities,
    "Application"  : Application,
    "Orderer"      : Orderer,
    "Channel"      : Channel,
    "Profiles"     : Profiles 

}


yaml.dump(configtx_dict, open("./temp.yaml", 'w'))

FileName = 'temp.yaml'

with open(FileName) as f:
    newText=f.read().replace('\\\"', '')
    newText=newText.replace('REMOVE_THIS_LINE', '')
    newText=newText.replace('\'\"', '\"')
    newText=newText.replace('\"\'', '\"')


with open(FileName, "w") as f:
    f.write(newText)
