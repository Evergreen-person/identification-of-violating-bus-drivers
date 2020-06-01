from math import hypot
from event import Event, EventType
from utils import get_center


class Bus:

    def __init__(self, track, frame_id, counter_to_change_state=20, min_distance=4.0, dist_persec=1, nn_age=10, fps=25):
        self.track_id = track.track_id
        init_box = track.to_tlbr()
        self.boxes = [init_box]
        self.centers = [get_center(
            init_box[0], init_box[1], init_box[2], init_box[3])]
        self.is_stopped = False
        self.counter = counter_to_change_state
        self.count_to_change_state = counter_to_change_state
        self.is_deleted = track.is_deleted()
        self.min_distance = min_distance
        self.dist_persec = dist_persec
        self.time_since_update = 0
        self.nn_age = nn_age
        self.events = []
        self.frames = [frame_id]
        self.fps = fps

    def get_last_meet(self):
        return self.frames[-1]

    def get_first_center_before_nsec_of_last(self, nsec):
        return list(filter(lambda x: x[1] > self.get_last_meet() - nsec*self.fps, zip(self.centers, self.frames)))[0][0]

    def update(self, track, frame_id):
        self.time_since_update = 0
        if track.is_deleted():
            self.is_deleted = True
        elif track.is_confirmed() and track.time_since_update == 0:
            self.is_deleted = False
            self.frames.append(frame_id)
            bbox = track.to_tlbr()
            self.boxes.append(bbox)
            self.centers.append(get_center(bbox[0], bbox[1], bbox[2], bbox[3]))
            is_stopped = False
            p1 = self.centers[-1]
            p2 = self.get_first_center_before_nsec_of_last(self.dist_persec)
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
                        self.events.append(
                            Event(self.get_last_meet(), self.track_id, EventType.BusStopping))
                    else:
                        self.events.append(
                            Event(self.get_last_meet(), self.track_id, EventType.BusMoving))

    def tick(self):
        if self.time_since_update >= self.nn_age and not self.is_deleted:
            self.is_deleted = True
        self.time_since_update += 1
