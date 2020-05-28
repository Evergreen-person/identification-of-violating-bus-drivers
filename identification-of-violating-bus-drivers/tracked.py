from addons.deep_sort.deep_sort import nn_matching
from addons.deep_sort.deep_sort.detection import Detection
from addons.deep_sort.deep_sort.tracker import Tracker
from addons.deep_sort.tools import generate_detections as gdet
from addons.deep_sort.deep_sort.detection import Detection as ddet

class Tracked:

    def __init__(self, name, model_filename, max_cosine_distance, nn_budget, constructor, max_age = 10):
        self.name = name
        self.values = {}
        metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
        self.encoder = gdet.create_box_encoder(model_filename, batch_size=1)
        self.tracker = Tracker(metric, max_age = max_age)
        self.constructor = constructor

    def update(self, frame, boxes, scores, frame_id):
        features = self.encoder(frame, boxes)
        detections = [Detection(bbox, score, feature) for bbox, score, feature in zip(boxes, scores, features)]
        self.tracker.predict()
        self.tracker.update(detections)
        for track in self.tracker.tracks:
            if not track.time_since_update > 1:
                if self.values.get(track.track_id) is None:
                    self.values[track.track_id] = self.constructor(track, frame_id)
                else:
                    self.values[track.track_id].update(track, frame_id)

    def tick(self):
        for value in self.values.values():
            value.tick()

    def events(self):
        events = []
        for value in self.values.values():
            events.extend(value.events)
        return events