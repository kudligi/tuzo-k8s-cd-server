import flask
import os
import subprocess
from subprocess import check_output as CO

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    res = subprocess.check_output(['ls'])
    print(res)
    return "<h1>"+ str(res) +"</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"

@app.route('/RBAC_init', methods=['GET'])
def RBAC_init():
    try:
        res = CO(['kubectl', 'create', '-f', './helm-rbac.yaml'])
    except:
        print("already initialised")
        res = "already initialised"
    print(res)
    #res1 = CO(['helm', '-init', '--service-account-tiller'])
    return res


@app.route('/helm_init', methods=['GET'])
def helm_init():
    try:
        res = CO(['helm', 'init', '--service-account', 'tiller'])
    except:
        print("already initialised")
        res = "already initialised"
    print(res)
    #res1 = CO(['helm', '-init', '--service-account-tiller'])
    return res

@app.route('/install_argo', methods=['GET'])
def install_argo():
    try:
        res = CO(['kubectl', 'create', 'namespace', 'argo'])
    except Exception:
        print("already created namespace argo")
        res = Exception
    finally:
        print("install argo namespace output\n", res)
    
    try:
        res = CO(['kubectl', 'apply', '-n', 'argo', '-f', 'https://raw.githubusercontent.com/argoproj/argo/v2.4.3/manifests/install.yaml'])
    except Exception:
        print("something went wrong installing argo", Exception)
        res="something went wrong installing argo"
    finally:
        print("install argo output\n", res)

    
    #res1 = CO(['helm', '-init', '--service-account-tiller'])
    return res

@app.route('/grant_admin_privilages', methods=['GET'])
def grant_admin_privilages():
    try:
        res = CO(['kubectl', 'create', 'rolebinding', 'default-admin', '--clusterrole=admin', '--serviceaccount=default:default'])
    except Exception:
        print("rolebinding already exists")
        res = Exception
    finally:
        print("create admin role binding\n", res)

    
    #res1 = CO(['helm', '-init', '--service-account-tiller'])
    return res

@app.route('/install_artifact_repo', methods=['GET'])
def install_artifact_repo():
    try:
        res = subprocess.call(['helm', 'install', 'stable/minio', '-n', 'argo-artifacts', '--set', 'service.type=LoadBalancer',  '--set', 'defaultBucket.enabled=true',  '--set', 'defaultBucket.name=my-bucket', '--set', 'persistence.enabled=false', '--set', 'fullnameOverride=argo-artifacts'])
    except Exception:
        print("artifact repo already esists")
        res = "Exception"
    finally:
        print("create admin role binding\n", res)

    
    #res1 = CO(['helm', '-init', '--service-account-tiller'])
    return res

@app.route('/update_argo_configmap', methods=['GET'])
def update_aro_configmap():
    try:
        res = CO(['kubectl', 'replace', 'cm', '-n', 'argo', 'workflow-controller-configmap', '-f', 'temp.yaml'])
    except :
        print("rolebinding already exists")
        res = "Exception"
    finally:
        print("configmap updated\n", res)

    
    #res1 = CO(['helm', '-init', '--service-account-tiller'])
    return res

@app.route('/generate_startup_artifacts', methods=['GET'])
def generate_startup_artifacts():
    try:
        res = CO(['./init.sh', './samples/simple/', './samples/chaincode/'], cwd = "../PIVT2/PIVT/fabric-kube")
    except :
        print("rolebinding already exists")
        res = "Exception"
    finally:
        print("startup artifacts generated\n", res)

    
    #res1 = CO(['helm', '-init', '--service-account-tiller'])
    return res

@app.route('/bring_up_components', methods=['GET'])
def bring_up_components():
    try:
        res = subprocess.run(['helm', 'install', './hlf-kube', '--name', 'hlf-kube', '-f', 'samples/simple/network.yaml', '-f', 'samples/simple/crypto-config.yaml'], cwd = "../PIVT2/PIVT/fabric-kube")
    except :
        print("rolebinding already exists")
        res = "Exception"
    finally:
        print("components up\n", res)

    
    #res1 = CO(['helm', '-init', '--service-account-tiller'])
    return str(res)

@app.route('/channel_flow', methods=['GET'])
def channel_flow():
    old = os.getcwd()
    os.chdir("../PIVT2/PIVT/fabric-kube")

    try:
        res = os.system(" helm template channel-flow/ -f samples/simple/network.yaml -f samples/simple/crypto-config.yaml | argo submit - --watch")
        #res = subprocess.run(['helm', 'template', 'channel-flow/', '-f', 'samples/simple/network.yaml', '-f', 'samples/simple/crypto-config.yaml', '|', 'argo', 'submit', '-', '--watch'], cwd = "../PIVT2/PIVT/fabric-kube")
    except :
        print("channel-flow-failure")
        res = "Exception"
    finally:
        print("channel-flow-success\n", res)

    os.chdir(old)

    
    #res1 = CO(['helm', '-init', '--service-account-tiller'])
    return str(res)

@app.route('/chaincode_flow', methods=['GET'])
def chaincode_flow():
    old = os.getcwd()
    os.chdir("../PIVT2/PIVT/fabric-kube")

    try:
        res = os.system(" helm template chaincode-flow/ -f samples/simple/network.yaml -f samples/simple/crypto-config.yaml | argo submit - --watch")
        #res = subprocess.run(['helm', 'template', 'channel-flow/', '-f', 'samples/simple/network.yaml', '-f', 'samples/simple/crypto-config.yaml', '|', 'argo', 'submit', '-', '--watch'], cwd = "../PIVT2/PIVT/fabric-kube")
    except :
        print("CHAINCODE-flow-failure")
        res = "Exception"
    finally:
        print("CHAINCODE-flow-success\n", res)

    os.chdir(old)

    
    #res1 = CO(['helm', '-init', '--service-account-tiller'])
    return str(res)

app.run()