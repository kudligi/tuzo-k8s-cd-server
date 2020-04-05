from flask import Flask, request, json
from flask_restplus import Api, Resource, reqparse
from cluster_utils import *
import generator_utils as G

app = Flask(__name__)
api = Api(app)

@api.route('/hello')
class HelloWorld(Resource):
    def get(self):
        return {"Hello":"World"}

@api.route('/cluster')
class ClusterOperations(Resource):
    def post(self):        
        parser = reqparse.RequestParser()
        parser.add_argument('operation', required=True, help="operation cannot be blank!")
        parser.add_argument('name', required=True, help="name cannot be blank!")
        args = parser.parse_args() 
        response = {}
        response["request_body"] = args

        if args['operation'] == 'create':
            response["payload"] = init_cluster(args["name"])
        else:
            response["payload"] = { "message" : "invalid_operation" }

        return response

@api.route('/hlf')
class HlfOperations(Resource):
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('config', required=True, help="config needs to be supplied")
        parser.add_argument('operation', required=True, help="operation needs to be supplied")

        args = parser.parse_args() 
        data = request.json["config"]
        
        
        if args["operation"] == "init":
            with open('./config_files/present_network/config.json', 'w') as f:
                json.dump(data, f, indent=4)
            G.create_cryptogen(data, "./config_files/upayan-hlf-kube/crypto-config.yaml")
            G.create_configtx(data, "./config_files/upayan-hlf-kube/configtx.yaml")
            G.create_network(data, "./config_files/upayan-hlf-kube/network.yaml")
            runWithOutput('cp -r ./config_files/upayan-hlf-kube ../fabric-kube-v2/upayan-fabric' )
            response = {'message' : 'initialized config.json and updated upayan-hlf-kube files', 'operation' : args['operation']}
        else:
            response = { 'message' : 'invalid operation' }
        
        return response

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('operation', required=True, help="operation needs to be supplied")

        args = parser.parse_args() 
        payload = {}
        result = {}
        if args["operation"] == "UP":
            runCommandsIn('../fabric-kube-v2', ['./init.sh ./upayan-fabric ./samples/chaincode/'])
            payload["create_files"] = "success"
            
            runCommandsIn('../fabric-kube-v2', ['helm install ./hlf-kube --name hlf-kube -f upayan-fabric/network.yaml -f upayan-fabric/crypto-config.yaml --set orderer.cluster.enabled=true --set peer.launchPods=false --set orderer.launchPods=false'])          
            payload["init network"] = "success"

            runCommandsIn('../fabric-kube-v2', ['./collect_host_aliases.sh ./upayan-fabric/'])          
            payload["collect host aliases"] = "success"
            
            runCommandsIn('../fabric-kube-v2', ['helm upgrade hlf-kube ./hlf-kube -f upayan-fabric/network.yaml -f upayan-fabric/crypto-config.yaml -f upayan-fabric/hostAliases.yaml --set orderer.cluster.enabled=true'])          
            payload["netowrk up"] = "success"

            t = myrunArgoWatch('../fabric-kube-v2','helm template channel-flow/ -f upayan-fabric/network.yaml -f upayan-fabric/crypto-config.yaml -f upayan-fabric/hostAliases.yaml | argo submit - --watch')
            print("channel flow\n", t)
            payload["channel-flow"] = {"message":t, "status":"success"}

            t = myrunArgoWatch('../fabric-kube-v2','helm template chaincode-flow/ -f upayan-fabric/network.yaml -f upayan-fabric/crypto-config.yaml -f upayan-fabric/hostAliases.yaml | argo submit - --watch')
            print("chaincode flow\n", t)
            payload["chaincode-flow"] = {"message":t, "status":"success"}
            
            # runCommandsIn('../fabric-kube-v2', ['helm upgrade hlf-kube ./hlf-kube -f upayan-fabric/network.yaml -f upayan-fabric/crypto-config.yaml -f upayan-fabric/hostAliases.yaml --set orderer.cluster.enabled=true'])          
            # payload["netowrk up"] = "success"
            result["operation"] = args["operation"]
            result["payload"] = payload
        else:
            result["operation"] = "invalid"
            result["payload"] = payload
        return result

    def get(self):
        try:
            payload = json.load(open("./config_files/present_network/config.json", "r"))
        except:
            response = { "payload" : {}, "error" : "no config exists" }
        else:
            response = { "payload" : payload }
        return response

        


if __name__ == '__main__':
    app.run(debug=True)