from flask import Flask
from flask_restful import Resource, Api, reqparse, abort
import os, sys, subprocess

app = Flask(__name__)
api = Api(app)

CLUSTERS = {}

parser = reqparse.RequestParser()
parser.add_argument('cluster_id')

class HelloWorld(Resource):
    def get(self):
        return {"hello" : "world"}

class Cluster(Resource):
    def get(self, cluster_id):
        return {"GET": cluster_id}

    def post(self, cluster_id):
        return {"POST": cluster_id}

api.add_resource(HelloWorld, "/")
api.add_resource(Cluster, "/cluster/<string:cluster_id>")

if __name__ == '__main__':
    app.run(debug=True) 