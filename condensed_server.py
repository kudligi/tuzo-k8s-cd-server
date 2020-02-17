import os
import flask
from flask import json, request
from flask_cors import CORS
import subprocess
from subprocess import check_output as CO

app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

def read_json(filename):
    with open(filename) as f:
        data = json.load(f)
        return data

@app.route('/', methods=['GET'])
def home():
    return("hello_world")


@app.route('/create_cluster', methods=['GET'])
def create_cluster():
    try:
        os.system('gcloud beta container --project "busy-burglar" clusters create "test-k8-1" --zone "asia-southeast1-b" --no-enable-basic-auth --cluster-version "1.13.11-gke.14" --machine-type "n1-standard-1" --image-type "COS" --disk-type "pd-standard" --disk-size "100" --scopes "https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" --num-nodes "8" --enable-cloud-logging --enable-cloud-monitoring --enable-ip-alias --network "projects/busy-burglar/global/networks/default" --subnetwork "projects/busy-burglar/regions/asia-southeast1/subnetworks/default" --default-max-pods-per-node "110" --addons HorizontalPodAutoscaling,HttpLoadBalancing --enable-autoupgrade --enable-autorepair')
    except Exception:
        print("something went wrong\n", Exception)
        return("SOS")
    
    return "all good cluster being created"

@app.route('/connect_cli_to_cluster', methods=['GET'])
def connect_cli_to_cluster():
    try:
        os.system('gcloud container clusters get-credentials test-k8-1')
    except Exception:
        print("something went wrong\n", Exception)
        return("SOS")
    
    return "cli initailised in server"

@app.route('/create_and_connect_to_cluster', methods=['GET'])
def ClusterInit():
    try:
        os.system('gcloud beta container --project "busy-burglar" clusters create "test-k8-1" --zone "asia-southeast1-b" --no-enable-basic-auth --cluster-version "1.13.11-gke.14" --machine-type "n1-standard-1" --image-type "COS" --disk-type "pd-standard" --disk-size "100" --scopes "https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" --num-nodes "8" --enable-cloud-logging --enable-cloud-monitoring --enable-ip-alias --network "projects/busy-burglar/global/networks/default" --subnetwork "projects/busy-burglar/regions/asia-southeast1/subnetworks/default" --default-max-pods-per-node "110" --addons HorizontalPodAutoscaling,HttpLoadBalancing --enable-autoupgrade --enable-autorepair')
        os.system('gcloud container clusters get-credentials test-k8-1')
    except:
        print("something went wrong") 
        return("something is wrong")
    return "cluster created and connected to"       
    

@app.route('/prep_cluster_step1', methods=['GET'])
def prep_cluster_step1():
    res = os.system("kubectl create -f ./helm-rbac.yaml")
    if res == 0:
        res = os.system("helm init --service-account tiller")
        res = os.system("kubectl create namespace argo")
        res = os.system("kubectl apply -n argo -f https://raw.githubusercontent.com/argoproj/argo/v2.4.3/manifests/install.yaml")

    return "done"

@app.route('/prep_cluster_step2', methods=['GET'])
def prep_cluster_step2():
    res = os.system("kubectl create rolebinding default-admin --clusterrole=admin --serviceaccount=default:default")
    res = os.system("helm install stable/minio -n argo-artifacts  --set service.type=LoadBalancer   --set defaultBucket.enabled=true   --set defaultBucket.name=my-bucket   --set persistence.enabled=false   --set fullnameOverride=argo-artifacts")

    return "done"


@app.route('/prep_cluster_step3', methods=['GET'])
def prep_cluster_step3():
    res = os.system("kubectl apply -f temp.yaml")

    return "done"


@app.route('/start_network1', methods=['GET'])
def start_network1():
    old = os.getcwd()
    os.chdir("../PIVT3/PIVT/fabric-kube")
    res = os.system("./init.sh ./samples/simple/ ./samples/chaincode/")
    res = os.system("helm install ./hlf-kube --name hlf-kube -f samples/simple/network.yaml -f samples/simple/crypto-config.yaml")
    os.chdir(old)
    res = os.system("rm -rf rm -rf node-app-files/channel/*")
    res = os.system("cp -R ../PIVT3/PIVT/fabric-kube/hlf-kube/crypto-config node-app-files/channel/")
    res = os.system("cp ../PIVT3/PIVT/fabric-kube/hlf-kube/channel-artifacts/* node-app-files/channel/")
    return "done"

@app.route('/start_network2', methods=['GET'])
def start_network2():
    old = os.getcwd()
    os.chdir("../PIVT3/PIVT/fabric-kube")
    res = os.system("helm template channel-flow/ -f samples/simple/network.yaml -f samples/simple/crypto-config.yaml | argo submit - --watch")
    res = os.system("helm template chaincode-flow/ -f samples/simple/network.yaml -f samples/simple/crypto-config.yaml | argo submit - --watch")

    os.chdir(old)
    return "done"



@app.route('/extend_network1', methods=['GET'])
def extend_network1():
    old = os.getcwd()
    os.chdir("../PIVT3/PIVT/fabric-kube")
    res = os.system("./extend.sh samples/simple")
    res = os.system("helm upgrade hlf-kube ./hlf-kube -f samples/simple/network.yaml -f samples/simple/crypto-config.yaml")
    os.chdir(old)
    res = os.system("rm -rf rm -rf node-app-files/channel/*")
    res = os.system("cp -R ../PIVT3/PIVT/fabric-kube/hlf-kube/crypto-config node-app-files/channel/")
    res = os.system("cp ../PIVT3/PIVT/fabric-kube/hlf-kube/channel-artifacts/* node-app-files/channel/")
    return "done"



@app.route('/extend_network2/<version>', methods=['GET'])
def extend_network2(version):
    old = os.getcwd()
    os.chdir("../PIVT3/PIVT/fabric-kube")
    res = os.system("helm template peer-org-flow/ -f samples/simple/network.yaml -f samples/simple/crypto-config.yaml -f samples/simple/configtx.yaml | argo submit - --watch")
    res = os.system("helm template channel-flow/ -f samples/simple/network.yaml -f samples/simple/crypto-config.yaml | argo submit - --watch")
    res = os.system("helm template chaincode-flow/ -f samples/simple/network.yaml -f samples/simple/crypto-config.yaml --set chaincode.version="+ version +" | argo submit - --watch")

    os.chdir(old)
    return "done"




@app.route('/scrap_network', methods=['GET'])
def scrap_network():
    old = os.getcwd()
    os.chdir("../PIVT3/PIVT/fabric-kube")
    res = os.system("helm del --purge hlf-kube")
    os.chdir(old)
    return "done"

@app.route('/set_net_json', methods=['POST'])
def set_net_json():
    net_json = request.get_json()
    with open("./config-files/generated_network_config/"+net_json["filename"], 'w') as outfile:
        json.dump(net_json["network_config"], outfile, sort_keys=True, indent=4)
    old = os.getcwd()
    os.chdir('./config-files/')
    os.system('python generate.py ' + net_json["filename"])
    os.chdir(old)
    return "done"

@app.route('/add_org_to_json', methods=['POST'])
def add_org_to_json():
    data = request.get_json()
    print(data)
    filename = data['filename']
    filepath = "./config-files/generated_network_config/" +  data["filename"]
    orgname = data["name"]
    domain = data["domain"]
    net = read_json(filepath)
    if orgname not in  net["Channels"][0]["orgs"]: 
        net["OtherOrganizations"].append({"name": orgname, "domain": domain})
        net["Channels"][0]["orgs"].append(orgname)
        with open(filepath, 'w') as outfile:
            json.dump(net, outfile, sort_keys=True, indent=4)

        old = os.getcwd()
        os.chdir('./config-files/')
        os.system('python generate.py ' + filename)
        os.chdir(old)
    else:
        return "org already exists with this name in network\n"
    return "done"



@app.route('/deploy_node_app', methods=['GET'])
def deploy_node_app():
    try:
        os.system("kubectl create deployment hello-web --image=gcr.io/busy-burglar/hello-app:v1")
        proc = subprocess.Popen(["kubectl get pods | grep hello | awk {'print $1'}"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        print(out)

    
    except:
        print("didnt finish something went wrong")
        return "didnt finish something went wrong"
    
    return "node app deployed"


@app.route('/migrate_connection_profile/<filename>', methods=['GET'])
def migrate_connection_profile(filename):
    try:
        os.system("cd ./node-app-files/ && python generate-common-profile.py " + filename)
        os.system("cd ./node-app-files/ && python generate-client-profiles.py " + filename)
        
        proc = subprocess.Popen(["kubectl get pods | grep hello | awk {'print $1'}"], stdout=subprocess.PIPE, shell=True)
        (pod_name, err) = proc.communicate()
        print(pod_name.decode("utf-8")[:-1])
        pod_name = pod_name.decode("utf-8")[:-1]
        print("kubectl cp network-config.yaml " + pod_name+":/home/nodejs/app/artifacts/")
        proc = subprocess.Popen(["kubectl cp node-app-files/network-config.yaml " + pod_name+":/home/nodejs/app/artifacts/"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        print(out)
        
        proc = subprocess.Popen(["kubectl cp node-app-files/org1.yaml " + pod_name+":/home/nodejs/app/artifacts/"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        print(out)

        proc = subprocess.Popen(["kubectl cp node-app-files/org2.yaml " + pod_name+":/home/nodejs/app/artifacts/"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        print(out)

        proc = subprocess.Popen(["kubectl cp node-app-files/channel/ " + pod_name+":/home/nodejs/app/artifacts/"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        print(out)
    
    except Exception:
        print("didnt finish something went wrong, ", str(Exception))
        return "didnt finish something went wrong"
    
    return "connection profiles moved to node app"





app.run()


