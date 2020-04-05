import os
import sys
import subprocess
import json

from kubernetes import client, config
from pprint import pprint
import time

config.load_kube_config()
v1 = client.CoreV1Api()
apps = client.AppsV1Api()


def wait_for_resource(name, namespace):
    start = time.time()
    while(True):
        try:
            res = apps.read_namespaced_deployment_status(name, namespace)
        except:
            print("Oops!",sys.exc_info()[0],"occured.")
            time.sleep(3)
        else:    
            pprint(res.status)
            if res.status.available_replicas == None:
                print("/n/n not yet avalialble")
                time.sleep(1)
            else:
                break

    end = time.time()
    return "up", end - start


def getCreateClusterCommand(cluster_name = "test-k8-cluster"):
    command = 'gcloud beta container --project busy-burglar clusters create {} --zone asia-southeast1-b --no-enable-basic-auth --cluster-version 1.14.10-gke.17 --machine-type n1-standard-1 --image-type COS --disk-type pd-standard --disk-size 100 --scopes https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append --num-nodes 8 --enable-stackdriver-kubernetes --enable-ip-alias --network projects/busy-burglar/global/networks/default --subnetwork projects/busy-burglar/regions/asia-southeast1/subnetworks/default --default-max-pods-per-node 110 --addons HorizontalPodAutoscaling,HttpLoadBalancing --enable-autoupgrade --enable-autorepair'.format(cluster_name)
    return command

def getClusterCredentialsCommand(cluster_name = "test-k8-cluster"):
    command = 'gcloud container clusters get-credentials {}'.format(cluster_name)
    return command

def getInitHelmRBACCommand():
    return "kubectl create -f ../cluster_resource_yaml-v2/helm-rbac.yaml && helm init --service-account tiller"

def getDeployArgoCommand():
    return "kubectl create namespace argo && kubectl apply -n argo -f https://raw.githubusercontent.com/argoproj/argo/v2.4.3/manifests/install.yaml"

def getDeployMinioCommand():
    return "kubectl create rolebinding default-admin --clusterrole=admin --serviceaccount=default:default && helm install stable/minio -n argo-artifacts  --set service.type=LoadBalancer   --set defaultBucket.enabled=true   --set defaultBucket.name=my-bucket   --set persistence.enabled=false   --set fullnameOverride=argo-artifacts && kubectl apply -f ../cluster_resource_yaml-v2/temp.yaml"


###############################################################
######################## Executing Shell Commands #############
###############################################################

def myrun(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = []
    i = 0
    while True:
        i+=1
        line = p.stdout.readline().decode('utf-8')
        stdout.append(line)
        print('output line {} '.format(i), line,)
        if p.poll() != None:
            break
    return ''.join(stdout)

def myrunArgoWatch(directory, cmd):
    old = os.getcwd()
    print("in directory :", os.getcwd())
    os.chdir(directory)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = []
    temp = []
    i = 0
    while True:
        i+=1
        line = p.stdout.readline().decode('utf-8')
        if "STEP" in line:
            print("OutputBlock is \n")
            for l in stdout:
                print(l)
            # temp = stdout.copy()
            stdout = []
        stdout.append(line)
        # print('output line {} '.format(i), line,)
        if p.poll() != None:
            break
    os.chdir(old)
    return ''.join(stdout)

def runWithOutput(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = []
    i = 0
    while True:
        i+=1
        line = p.stdout.readline().decode('utf-8')
        stdout.append(line)
        print('output line {} '.format(i), line,)
        if p.poll() != None:
            break
    return ''.join(stdout)


    
def runCommandsIn(directory, commands):
    old = os.getcwd()
    print("in directory :", os.getcwd())
    os.chdir(directory)
    print("in directory :", os.getcwd())
    for command in commands:
        print("RUNNING COMMAND\n")
        print(command + "\n")
        runWithOutput(command)
    os.chdir(old)
    print("in directory :", os.getcwd())

def create_cluster(name):
    cmd = getCreateClusterCommand(name)
    response = myrun(cmd)
    result = {}
    if "ERROR" in response:
        result["error"] = response
        result["status"] = "failed"
        result["message"] = "CLuster could not be created"
        raise Exception(json.dumps(result))
    result["status"] = "success"
    result["message"] = "Create cluster succeded"
    result["response"] = response
    return result

def init_cluster(name):
    # create cluster
    s = time.time()
    res = {}
    try:   
        t = create_cluster(name)
        res["cluster_create"] = {"cluster_created" : "yes", "response" : "t"}
    except Exception as e:
        res["create_cluster"] = {"error" : str(e), "status" : "failed" }
        
    
    # init cluster credentials
    t = myrun(getClusterCredentialsCommand(name))
    if "ERROR" in t:
        res["init_cluster_credentials"] = { "status" : "failed", "error" : t }
    
    else:
        res["init_cluster_credentials"] = { "status" : "succeded", "message" : t}
    
    # init Role Based Access Control
    t = myrun(getInitHelmRBACCommand())
    if "Error" in t:
        res["init_RBAC"] = { "status" : "failed" , "error" : t }
    else:
        res["init_RBAC"] = { "status" : "succeded" , "message" : t }

    # deploy Argo-worlflow controller
    t = myrun(getDeployArgoCommand())
    if "Error" in t:
        res["init_argo_controller"] = { "status" : "failed", "error" : t }
    else:
        res["init_argo_controller"] = { "status" : "succeded" , "message" : t }

    time.sleep(4)
    res["init_argo_controller"]["availability"] = wait_for_resource("argo-ui", "argo")

    t = myrun(getDeployMinioCommand())
    if "Error" in t:
        res["create-minio-buckets"] = { "status" : "failed", "error" : t }
    else:
        res["create-minio-buckets"] = { "status" : "succeded" , "message" : t }
    
    
    res["time_taken"] = time.time() - s 
    
    return res
# print(myrun(getDeployArgoCommand()))
# print(myrun(getCreateClusterCommand()))
# print(myrun(getClusterCredentialsCommand()))
# print(myrun(getInitHelmRBACCommand()))
# print(myrun(getDeployArgoCommand()))
# print(myrun(getDeployMinioCommand()))
# runCommandsIn('../', ["ls", "pwd"])
# output = myrun(getCreateClusterCommand())
# if 'ERROR' in output:
#     print("FAILED OUTPUT is ", output)
# else:
#     print("SUCCESS OUTPUT is ",)



