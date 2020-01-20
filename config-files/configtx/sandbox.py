import json
import pprint
from ruamel.yaml import YAML
yaml = YAML()
import sys
pp = pprint.PrettyPrinter(indent=4)
import copy



data = yaml.load(open('configtx.yaml'))

data2 = yaml.load(open('temp.yaml'))

pp.pprint(data["Profiles"]["OrdererGenesis"])
pp.pprint(data2["Profiles"]["OrdererGenesis"])