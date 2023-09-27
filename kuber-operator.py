from kubernetes import client, config
from flask import Flask, render_template, jsonify
import sys, os


# Replace with your custom annotations
annotations_to_watch = ["domainmanager.pegah.tech/requested-by", "domainmanager.pegah.tech/domain-usecase", "domainmanager.pegah.tech/ticket-id"]

app = Flask(__name__)

def get_ingresses_with_annotations():
    try:
        try:
            config.load_kube_config(context="stg")
        except:
            config.load_incluster_config()  # Load in-cluster config
        networking_v1 = client.NetworkingV1Api()
        ingresses = networking_v1.list_ingress_for_all_namespaces().items

        ingresses_with_annotations = []
        for ingress in ingresses:
            if ingress.spec.rules == None:
                print("[WARN] Ingress " + ingress.metadata.namespace + "/" + ingress.metadata.name + " is invalid")
                continue
            
            ingress_classname = "N/A"
            if ingress.spec.ingress_class_name: ingress_classname = ingress.spec.ingress_class_name
            for host in ingress.spec.rules:
                annotations = ingress.metadata.annotations
                ingress_info = {
                        "namespace": ingress.metadata.namespace,
                        "host": host.host,
                        "ingressClassName": ingress_classname,
                        "annotations": {}
                }
                if annotations:
                    for annotation in annotations_to_watch:
                        if annotation in annotations:
                            ingress_info["annotations"][annotation.replace("domainmanager.pegah.tech/", "")] = annotations[annotation]
                ingresses_with_annotations.append(ingress_info)
        return ingresses_with_annotations
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return {"error": f"Error retrieving Ingress resources: {e}"}

@app.route('/ingresses', methods=['GET'])
def ingresses():
    ingresses = get_ingresses_with_annotations()
    return render_template('ingresses.html', ingresses=ingresses, annotations_to_watch=annotations_to_watch)

@app.route('/ingresses-json', methods=['GET'])
def ingresses_json():
    ingresses = get_ingresses_with_annotations()
    return jsonify(ingresses)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
