from kubernetes import client, config
from pprint import pprint
import sys
import time

config.load_kube_config()

v1 = client.CoreV1Api()

apps = client.AppsV1Api()

# print("Listing pods with their IPs:")
# ret = v1.list_pod_for_all_namespaces(watch=False)
# for i in ret.items:
#     print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))





# while("true"):
#     try:
#         res = apps.read_namespaced_deployment_status('argo-ui', 'argo')
#     except:
#         print("Oops!",sys.exc_info()[0],"occured.")
#         time.sleep(3)
#     else:    
#         pprint(res.status)
#         if res.status.available_replicas == None:
#             print("/n/n not yet avalialble")
#             time.sleep(1)
#         else:
#             break

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

# res = apps.read_namespaced_stateful_set_status('hlf-peer--merchant1--peer0', 'default')
# pprint(res.status)


# res = apps.read_namespaced_deployment_status('hello-web', 'default')
# pprint(res.status)
