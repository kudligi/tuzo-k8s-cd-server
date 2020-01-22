

# Installation

## Create GKE cluster

## Connect Kubectl to cluster

## Prepare Cluster

### STEP 1 - install helm on gke [helm version - 2.16.1]
```sh
$ kubectl create -f ./helm-rbac.yaml
$ helm init --service-account tiller
```
### STEP 2 - install argo ui and controller on GKE
```sh
$ kubectl create namespace argo
$ kubectl apply -n argo -f https://raw.githubusercontent.com/argoproj/argo/v2.4.3/manifests/install.yaml
```
### STEP 3 - grant andmin privilages to default Service Account
```sh
$ kubectl create rolebinding default-admin --clusterrole=admin --serviceaccount=default:default
``` 

### STEP 4 - Install artifact Repository
```sh
$  helm install stable/minio -n argo-artifacts  --set service.type=LoadBalancer   --set defaultBucket.enabled=true   --set defaultBucket.name=my-bucket   --set persistence.enabled=false   --set fullnameOverride=argo-artifacts
``` 

### STEP 5 - edit configmap to point to the minio bucket for artifacts

```sh
 $ KUBE_EDITOR="nano" kubectl edit cm -n argo workflow-controller-configmap
 ```
 
 Copy and paste and save
 ```txt
 data:
  config: |
    artifactRepository:
      s3:
        bucket: my-bucket
        endpoint: argo-artifacts:9000
        insecure: true
        # accessKeySecret and secretKeySecret are secret selectors.
        # It references the k8s secret named 'argo-artifacts'
        # which was created during the minio helm install. The keys,
        # 'accesskey' and 'secretkey', inside that secret are where the
        # actual minio credentials are stored.
        accessKeySecret:
          name: argo-artifacts
          key: accesskey
        secretKeySecret:
          name: argo-artifacts
          key: secretkey
 ```

## Steps to deploy hlf


### Create Necessary stuff [certs / genesis block / transaction]
```sh
$ ./init.sh ./samples/simple/ ./samples/chaincode/
``` 

### Lauch Components of the Network
```sh
$ helm install ./hlf-kube --name hlf-kube -f samples/simple/network.yaml -f samples/simple/crypto-config.yaml
``` 

### FLOW 1 - CHANNEL FLOW 
Create channels, join peers to channels and update channels for Anchor peers - 
```sh
$ helm template channel-flow/ -f samples/simple/network.yaml -f samples/simple/crypto-config.yaml | argo submit - --watch
``` 

### FLOW 2 - CHAINCODE FLOW
Install/instantiate/invoke chaincodes -
```sh
$ helm template chaincode-flow/ -f samples/simple/network.yaml -f samples/simple/crypto-config.yaml | argo submit - --watch
``` 

## Steps to deploy hlf
### Add new Peer Org ----> Merchant with infra

#### EDIT CONFIG FILES
    1) network.yaml - automated 
    2) crypto-config.yaml - automated
    3) configtx.yaml - TODO
    
### Create Necessary certs / updated config block / transaction
```sh
$ ./extend.sh samples/simple
```
### Update crypto materials and components on fabric network
```sh
helm upgrade hlf-kube ./hlf-kube -f samples/simple/network.yaml -f samples/simple/crypto-config.yaml
```

### PEER ORG FLOW to add logically new org to Netowrk
```sh
$ helm template peer-org-flow/ -f samples/simple/network.yaml -f samples/simple/crypto-config.yaml -f samples/simple/configtx.yaml | argo submit - --watch
```

### CHANNEL-FLOW
```sh
$ helm template channel-flow/ -f samples/simple/network.yaml -f samples/simple/crypto-config.yaml | argo submit - --watch
```


### CHAINCODE FLOW
```sh
helm template chaincode-flow/ -f samples/simple/network.yaml -f samples/simple/crypto-config.yaml --set chaincode.version=2.0 | argo submit - --watch
```

## Add new peer node to existing Organization

### EDIT CONFIG FILE
    1) crypto-config.yaml

### Follow same steps as new Org [Skip Step PEER-ORG FLOW]


https://cloud.google.com/kubernetes-engine/docs/tutorials/hello-app

https://www.sitepoint.com/kubernetes-deploy-node-js-docker-app/

expose service from k8s dashboard

 
    





