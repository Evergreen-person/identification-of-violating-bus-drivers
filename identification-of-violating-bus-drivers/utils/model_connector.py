import json
import numpy as np
import requests


def predict(frame):
    frame_expanded = np.expand_dims(frame, axis=0)
    data = json.dumps({"signature_name": "serving_default",
                       "instances": frame_expanded.tolist()})
    headers = {"content-type": "application/json"}
    json_response = requests.post('http://localhost:8501/v1/models/faster_rcnn:predict',
                                  data=data, headers=headers)
    return np.array(json.loads(json_response.text)["predictions"])

# convert normalized box [ymin, xmin, ymax, xmax] to scaled [left upper x, left upper y, width, height]
def reshape_boxes(boxes, width, heigth):
    return [(xmin * width, ymin * heigth, (xmax - xmin) * width, (ymax - ymin) * heigth) for (ymin, xmin, ymax, xmax) in boxes]
