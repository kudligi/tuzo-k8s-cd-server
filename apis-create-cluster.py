import flask
import os
import subprocess
from subprocess import check_output as CO

app = flask.Flask(__name__)
app.config["DEBUG"] = True

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
app.run()

