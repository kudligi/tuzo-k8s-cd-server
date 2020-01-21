import os

os.chdir('./crypto-config')
os.system('python gen-file.py')
os.system('cp temp.yaml ../config_files/crypto-config.yaml')
os.chdir('..')

os.chdir('configtx')
os.system('python gen-file.py')
os.system('cp temp.yaml ../config_files/configtx.yaml')
os.chdir('..')

os.chdir('network')
os.system('python gen-file.py')
os.system('cp temp.yaml ../config_files/network.yaml')
os.chdir('..')


os.chdir('../../PIVT3/PIVT/fabric-kube/samples/simple')
os.system('rm *.yaml')
os.system('echo hello')
os.chdir('../../../../../k8-py-client/config-files')
os.system('cp config_files/* ../../PIVT3/PIVT/fabric-kube/samples/simple/')