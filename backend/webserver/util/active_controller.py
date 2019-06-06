import requests
import json
import yaml
import os

from database import AnnotationModel, ImageModel, DatasetModel, fix_ids

HEADERS = {'Content-Type': 'application/json', 'Accept':'application/json'}

URL_INIT_DATASET = "http://pcps-55.cirad.fr:9050/database/init"
URL_IMAGE = "http://pcps-55.cirad.fr:9050/database/image"
URL_ANNOTATION = "http://pcps-55.cirad.fr:9050/database/annotation"
URL_MODEL = "http://pcps-55.cirad.fr:9050/model/"

payload = {
        'config_cfg': ['MODEL.WEIGHT', '/home/user', 'OUTPUT_DIR', '/home/user', 'MODEL.ROI_BOX_HEAD.NUM_CLASSES', 4]
    }

def init_dataset(name, db_categories):
    categories = []
    for idx, category in enumerate(fix_ids(db_categories), 1):
        category['metadata']['coco_id'] = category['id']
        category['id'] = idx
        categories.append(category)
    payload = {
        'name': name,
        'categories': categories
    }
    requests.post(URL_INIT_DATASET, data=json.dumps(payload), headers=HEADERS)

def change_dataset(name):
    payload = {
        'name': name
    }
    requests.put(URL_INIT_DATASET, data=json.dumps(payload), headers=HEADERS)

def insert_image(path):
    image = fix_ids(ImageModel.objects(path=path).only(*ImageModel.COCO_PROPERTIES))[0]
    payload = {
        'image_info': {
                    'id': image['id'],
                    'file_name': image['file_name'],
                    'path': image['path'],
                    'width': image['width'],
                    'height': image['height'],
                    'metadata': image['metadata']
                }
    }
    requests.post(URL_IMAGE, data=json.dumps(payload), headers=HEADERS)

def delete_object(object_id, instance):
    if instance == 'annotation':
        annotation = AnnotationModel.objects(id=object_id).first()
        metadata = annotation.metadata
        if 'id_db' in metadata:
            payload = {
                'annotation_id': metadata['id_db'],
                'image_id': annotation.image_id
            }
            requests.delete(URL_ANNOTATION, params=payload)
    if instance == 'image':
        payload = {
            'image_id': object_id
        }
        requests.delete(URL_IMAGE, params=payload)

def get_predictions():
    r = requests.get(URL_MODEL, headers=HEADERS)
    r = r.content.decode('utf8').replace("'", '"')
    data = json.loads(r)
    return data['predictions']
    
def update_annotations_to_Arango(dataset_id):
    dataset = DatasetModel.objects(id=dataset_id).first()
    annotations = dataset.get_locked_annotations()
    for data in annotations:
        requests.put(URL_IMAGE, data=json.dumps(data), headers=HEADERS)

def make_predictions(dataset_id):
    update_annotations_to_Arango(dataset_id)
    # requests.post(URL_MODEL, headers=HEADERS)

def update_model(dataset_id):
    update_annotations_to_Arango(dataset_id)
    requests.put(URL_MODEL, headers=HEADERS)