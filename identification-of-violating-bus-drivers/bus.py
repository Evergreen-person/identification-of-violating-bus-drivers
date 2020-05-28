from math import hypot
from event import Event, EventType


class Bus:

    def __init__(self, track, frame_id, counter_to_change_state = 20, min_distance = 4.0, last_points = 2, age = 10):
        self.track_id = track.track_id
        init_box = track.to_tlbr()
        self.boxes = [init_box]
        self.centers = [(int(((init_box[0])+(init_box[2]))/2), int(((init_box[1])+(init_box[3]))/2))]
        self.is_stopped = False
        self.counter = counter_to_change_state
        self.count_to_change_state = counter_to_change_state
        self.is_deleted = track.is_deleted()
        self.min_distance = min_distance
        self.last_points = last_points
        self.time_since_update = 0
        self.frame_now = frame_id
        self.age = age
        self.events = []

    def update(self, track, frame_id):
        self.time_since_update = 0
        self.frame_now = frame_id
        if track.is_deleted():
            self.is_deleted = True
        elif track.is_confirmed() and track.time_since_update <= 1:
            self.is_deleted = False
            bbox = track.to_tlbr()
            self.boxes.append(bbox)
            self.centers.append((int(((bbox[0])+(bbox[2]))/2), int(((bbox[1])+(bbox[3]))/2)))
            is_stopped = False
            if len(self.centers) > self.last_points:
                p1 = self.centers[len(self.centers) - 1]
                p2 = self.centers[len(self.centers) - self.last_points]
                if hypot(p1[0] - p2[0], p1[1] - p2[1]) < self.min_distance * (bbox[2] - bbox[0]):
                    is_stopped = True
            if self.is_stopped is is_stopped:
                if self.counter < self.count_to_change_state:
                    self.counter += 1
            else:
                if self.counter > 0:
                    self.counter -= 1
                else:
                    self.is_stopped = not self.is_stopped
                    self.counter = self.count_to_change_state
                    if self.is_stopped:
                        self.events.append(Event(self.frame_now, self.track_id, EventType.BusStopping))
                    else:
                        self.events.append(Event(self.frame_now, self.track_id, EventType.BusMoving))
    def tick(self):
        if self.time_since_update >= self.age and not self.is_deleted:
            self.is_deleted = True
        self.time_since_update += 1