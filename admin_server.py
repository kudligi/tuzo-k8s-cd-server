import os
import flask
from flask import json, request, jsonify
from flask_cors import CORS
import subprocess
from subprocess import check_output as CO
import time
import datetime

from kubernetes import client, config
from pprint import pprint

from flask_restx import Api, Resource, fields


app = flask.Flask(__name__)
api = Api(app, verion='1.0', title='Upayan-Admin-Api', description="Admin Api for Upayan Loyalty Platform")

ns = api.namespace('admin', description= 'Admin Operations')

CORS(app)
app.config['DEBUG'] = True

response_json = {
    "program" : "admin_server",
    "version" : "TEST",
}

def populate_response(resp = response_json, status = "No info", code = "100", message = "message was not set", data = {}):
    # resp["program"] = "admin_server";
    # resp["version"] = "TEST";
    resp["datetime"] = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    resp["status"] = status
    resp["code"] = code
    resp["data"] = data
    resp["message"] = message
    return resp


def read_json(filename):
    with open(filename) as f:
        data = json.load(f)
        return data

# @app.route('/', methods=['GET'])
# def home():
#     resp = populate_response(status = "success", code = "200")
#     return resp

@ns.route('/hello')
class home(Resource):
    def get(self):
        resp = populate_response(status = "success", code = "200")
        return resp

cluster = api.model("cluster", {"name": fields.String(readonly=True, description='Name of the cluster')})

@ns.route('/cluster')
class cluster(Resource):
    @ns.doc('get cluster status')
    def get(self):
        resp = populate_response(status = "success", code = "200", message = "get cluster")
        return resp
    @ns.doc('create cluster')
    @ns.expect(cluster)
    def post(self):
        # message = request.form['message']
        resp = populate_response(status = "success", code = "200", message = message)
        return resp
# @app.route('/cluster', methods=['POST'])


app.run(port=9997)