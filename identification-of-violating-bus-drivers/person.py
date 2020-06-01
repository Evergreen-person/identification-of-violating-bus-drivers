from event import Event, EventType
from utils import get_center


class Person:

    def __init__(self, track, frame_id, nnage=10, fps=25):
        self.track_id = track.track_id
        init_box = track.to_tlbr()
        self.boxes = [init_box]
        self.centers = [get_center(
            init_box[0], init_box[1], init_box[2], init_box[3])]
        self.frames = [frame_id]
        self.is_deleted = track.is_deleted()
        self.is_confirmed = track.is_confirmed
        self.time_since_update = 0
        self.crossed = []
        self.nnage = nnage
        self.events = []
        self.fps = fps

    def get_first_meet(self):
        return self.frames[0]

    def get_last_meet(self):
        return self.frames[-1]

    def update(self, track, frame_id):
        self.time_since_update = 0
        if track.is_deleted():
            self.is_confirmed = False
            self.is_deleted = True
        elif track.time_since_update == 0:
            bbox = track.to_tlbr()
            self.boxes.append(bbox)
            self.centers.append(get_center(bbox[0], bbox[1], bbox[2], bbox[3]))
            self.is_confirmed = track.is_confirmed()
            self.frames.append(frame_id)
            self.is_deleted = False

    def set_crossed(self, bus_id, frame_id, doors_side):
        self.crossed.append({
            'bus_id': bus_id,
            'frame_id': frame_id,
            'door_side': doors_side
        })

    def check_outgoing_side(self, cross, pertime=1):
        p0 = self.centers[0]
        p1 = self.get_first_center_after_nsec_of_first(pertime)
        if cross['door_side'] == 'right':
            return p1[0] - p0[0] > 0
        elif cross['door_side'] == 'left':
            return p1[0] - p0[0] < 0
        else:
            return False

    def get_first_center_before_nsec_of_last(self, nsec):
        return list(filter(lambda x: x[1] > self.get_last_meet() - nsec*self.fps, zip(self.centers, self.frames)))[0][0]

    def get_first_center_after_nsec_of_first(self, nsec):
        return list(filter(lambda x: x[1] < self.get_first_meet() + nsec*self.fps, zip(self.centers, self.frames)))[-1][0]

    def check_ingoing_side(self, cross, pertime=1):
        p0 = self.centers[-1]
        p1 = self.get_first_center_before_nsec_of_last(pertime)
        if cross['door_side'] == 'right':
            return p1[0] - p0[0] > 0
        elif cross['door_side'] == 'left':
            return p1[0] - p0[0] < 0
        else:
            return False

    def check(self):
        for first_crossed in self.crossed[:1]:
            if (first_crossed['frame_id'] == self.get_first_meet()) and self.check_outgoing_side(first_crossed):
                self.events.append(Event(
                    first_crossed['frame_id'], self.track_id, EventType.PersonGoingOut, first_crossed["bus_id"]))
                break
        for last_crossed in reversed(self.crossed[-1:]):
            if (last_crossed['frame_id'] == self.get_last_meet()) and self.check_ingoing_side(last_crossed):
                self.events.append(Event(self.get_last_meet(
                ), self.track_id, EventType.PersonGoingInto, last_crossed["bus_id"]))
                break

    def tick(self):
        if self.time_since_update >= self.nnage and not self.is_deleted:
            self.is_deleted = True
            self.check()
        self.time_since_update += 1
